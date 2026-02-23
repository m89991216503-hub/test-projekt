import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException

import config


def send_email(from_addr: str, to_addr: str, subject: str, body: str) -> None:
    """Send an email via SMTP using settings from config."""
    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        raise HTTPException(status_code=503, detail="SMTP not configured")

    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
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
