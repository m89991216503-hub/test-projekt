from __future__ import annotations

import asyncio
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import config
from models import EmailMessage, User
from utils.crypto import decrypt_password


def _smtp_send(smtp_user: str, smtp_password: str, to_addr: str, subject: str, body: str) -> None:
    """Synchronous SMTP send using per-user credentials — runs in a thread."""
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        if config.MAIL_SMTP_USE_TLS:
            server = smtplib.SMTP(config.MAIL_SMTP_HOST, config.MAIL_SMTP_PORT, timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(config.MAIL_SMTP_HOST, config.MAIL_SMTP_PORT, timeout=10)

        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_addr, msg.as_string())
        server.quit()
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(status_code=502, detail="Mail authentication failed")
    except (smtplib.SMTPException, OSError):
        raise HTTPException(status_code=502, detail="Mail server unavailable")


async def send_email(
    user: User,
    to_addr: str,
    subject: str,
    body: str,
    db: AsyncSession,
) -> None:
    """Send email via the user's personal SMTP account and save a copy to the database."""
    if not config.MAIL_SMTP_HOST:
        raise HTTPException(status_code=503, detail="SMTP not configured")

    if not user.mail_password:
        raise HTTPException(status_code=503, detail="Почтовый ящик пользователя не создан")

    smtp_password = decrypt_password(user.mail_password)
    await asyncio.to_thread(_smtp_send, user.mail_address, smtp_password, to_addr, subject, body)

    db.add(EmailMessage(
        user_id=user.id,
        direction="sent",
        from_addr=user.mail_address,
        to_addr=to_addr,
        subject=subject,
        body=body,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        is_read=True,
    ))
    await db.commit()
