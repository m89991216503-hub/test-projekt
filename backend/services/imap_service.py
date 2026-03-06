import asyncio
import imaplib
import email as email_lib
from datetime import datetime, timezone
from email.header import decode_header
from email.utils import parsedate_to_datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import config
from models import EmailMessage, User


def _safe_charset(charset: Optional[str]) -> str:
    """Map non-standard or unknown charset names to something Python can handle."""
    if not charset:
        return "utf-8"
    try:
        import codecs
        codecs.lookup(charset)
        return charset
    except LookupError:
        return "latin-1"


def _decode_str(value: str) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            result.append(part.decode(_safe_charset(charset), errors="replace"))
        else:
            result.append(part)
    return "".join(result)


def _extract_body(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                charset = _safe_charset(part.get_content_charset())
                return payload.decode(charset, errors="replace")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                charset = _safe_charset(part.get_content_charset())
                return payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = _safe_charset(msg.get_content_charset())
            return payload.decode(charset, errors="replace")
    return ""


def _fetch_from_imap(existing_uids: set) -> list:
    """Synchronous IMAP fetch — intended to run in a thread."""
    messages = []
    try:
        if config.IMAP_USE_SSL:
            mail = imaplib.IMAP4_SSL(config.IMAP_HOST, config.IMAP_PORT)
        else:
            mail = imaplib.IMAP4(config.IMAP_HOST, config.IMAP_PORT)

        mail.login(config.IMAP_USER, config.IMAP_PASSWORD)
        mail.select("INBOX")

        _, data = mail.uid("search", None, "ALL")
        all_uids = data[0].split() if data[0] else []
        new_uids = [uid for uid in all_uids if int(uid) not in existing_uids]
        # Fetch only the latest 50 new messages to avoid long delays
        new_uids = new_uids[-50:]

        for uid_bytes in new_uids:
            uid = int(uid_bytes)
            _, msg_data = mail.uid("fetch", uid_bytes, "(RFC822)")
            if not msg_data or not isinstance(msg_data[0], tuple):
                continue
            raw = msg_data[0][1]
            if not isinstance(raw, bytes):
                continue
            msg = email_lib.message_from_bytes(raw)

            from_addr = _decode_str(msg.get("From", ""))
            to_addr = _decode_str(msg.get("To", ""))
            subject = _decode_str(msg.get("Subject", "(без темы)")) or "(без темы)"
            date_str = msg.get("Date", "")

            try:
                created_at = parsedate_to_datetime(date_str)
                if created_at.tzinfo is not None:
                    created_at = created_at.astimezone(timezone.utc).replace(tzinfo=None)
            except Exception:
                created_at = datetime.utcnow()

            messages.append({
                "uid": uid,
                "from_addr": from_addr,
                "to_addr": to_addr,
                "subject": subject,
                "body": _extract_body(msg),
                "created_at": created_at,
            })

        mail.logout()

    except imaplib.IMAP4.error as e:
        raise HTTPException(status_code=502, detail=f"IMAP error: {e}")
    except OSError:
        raise HTTPException(status_code=503, detail="Mail server unavailable")

    return messages


async def fetch_inbox(db: AsyncSession, users: list, fallback_user_id: Optional[int] = None) -> int:
    if not config.IMAP_USER or not config.IMAP_PASSWORD:
        raise HTTPException(status_code=503, detail="IMAP not configured")

    result = await db.execute(
        select(EmailMessage.imap_uid).where(EmailMessage.imap_uid.is_not(None))
    )
    existing_uids = {row[0] for row in result.all()}

    user_map = {u.email.lower(): u.id for u in users}
    if fallback_user_id is None:
        fallback_user_id = next((u.id for u in users if u.is_admin), None)
    if fallback_user_id is None and users:
        fallback_user_id = users[0].id

    new_messages = await asyncio.to_thread(_fetch_from_imap, existing_uids)

    count = 0
    for m in new_messages:
        to_lower = m["to_addr"].lower()
        user_id = next(
            (uid for email, uid in user_map.items() if email in to_lower),
            fallback_user_id,
        )
        if user_id is None:
            continue

        db.add(EmailMessage(
            user_id=user_id,
            direction="recv",
            from_addr=m["from_addr"],
            to_addr=m["to_addr"],
            subject=m["subject"],
            body=m["body"],
            created_at=m["created_at"],
            is_read=False,
            imap_uid=m["uid"],
        ))
        count += 1

    if count > 0:
        await db.commit()

    return count
