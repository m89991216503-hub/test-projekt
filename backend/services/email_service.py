import asyncio
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import config
from models import EmailMessage


def _smtp_send(from_addr: str, to_addr: str, subject: str, body: str) -> None:
    """Synchronous SMTP send — intended to run in a thread."""
    msg = MIMEMultipart()
    msg["From"] = config.SMTP_USER
    msg["To"] = to_addr
    msg["Subject"] = subject
    # If sending from a different address, add Reply-To so replies go there
    if from_addr != config.SMTP_USER:
        msg["Reply-To"] = from_addr
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        if config.SMTP_USE_TLS:
            server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, timeout=10)

        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(status_code=502, detail="Mail authentication failed")
    except (smtplib.SMTPException, OSError):
        raise HTTPException(status_code=502, detail="Mail server unavailable")


async def send_email(
    from_addr: str,
    to_addr: str,
    subject: str,
    body: str,
    user_id: int,
    db: AsyncSession,
) -> None:
    """Send email via SMTP and save a copy to the database."""
    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        raise HTTPException(status_code=503, detail="SMTP not configured")

    await asyncio.to_thread(_smtp_send, from_addr, to_addr, subject, body)

    db.add(EmailMessage(
        user_id=user_id,
        direction="sent",
        from_addr=from_addr,
        to_addr=to_addr,
        subject=subject,
        body=body,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        is_read=True,
    ))
    await db.commit()
