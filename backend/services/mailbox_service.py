from __future__ import annotations

import os
import secrets
import subprocess
from typing import Optional

from passlib.hash import sha512_crypt

import config
from utils.crypto import encrypt_password

_DOVECOT_SCHEME = "SHA512-CRYPT"
_MAIL_UID = 5000
_MAIL_GID = 5000


def _make_dovecot_hash(password: str) -> str:
    return "{" + _DOVECOT_SCHEME + "}" + sha512_crypt.hash(password)


async def create_mailbox(username: str) -> Optional[str]:
    """
    Creates a virtual mailbox username@MAIL_DOMAIN.

    Supports two backends (checked in order):
      1. DOVECOT_PASSWD_FILE — appends entry to Dovecot passwd-file and
         creates the mail directory (Postfix+Dovecot with passwd-file setup).
      2. MAIL_DB_URL — inserts row into Postfix/Dovecot MySQL virtual_users table.

    Returns encrypted mail password for storage in User.mail_password.
    Returns None if neither backend is configured (registration proceeds without a mailbox).
    """
    passwd_file = config.DOVECOT_PASSWD_FILE
    if passwd_file:
        return await _create_mailbox_passwdfile(username, passwd_file)

    if config.MAIL_DB_URL:
        return await _create_mailbox_mysql(username)

    return None


async def _create_mailbox_passwdfile(username: str, passwd_file: str) -> Optional[str]:
    email = f"{username}@{config.MAIL_DOMAIN}"
    plain_password = secrets.token_urlsafe(20)
    dovecot_hash = _make_dovecot_hash(plain_password)
    mail_home = f"/var/mail/vhosts/{config.MAIL_DOMAIN}/{username}"

    try:
        # Skip if user already exists
        if os.path.exists(passwd_file):
            with open(passwd_file, "r") as f:
                for line in f:
                    if line.startswith(email + ":"):
                        return None

        # Append to passwd file
        entry = f"{email}:{dovecot_hash}:{_MAIL_UID}:{_MAIL_GID}::{mail_home}::\n"
        with open(passwd_file, "a") as f:
            f.write(entry)

        # Create mailbox directory
        os.makedirs(mail_home, mode=0o770, exist_ok=True)
        os.chown(mail_home, _MAIL_UID, _MAIL_GID)

        # Signal Dovecot to reload user list
        subprocess.run(["doveadm", "reload"], capture_output=True)

    except Exception:
        return None

    return encrypt_password(plain_password)


async def _create_mailbox_mysql(username: str) -> Optional[str]:
    import aiomysql
    from urllib.parse import urlparse

    plain_password = secrets.token_urlsafe(20)
    dovecot_hash = _make_dovecot_hash(plain_password)
    email = f"{username}@{config.MAIL_DOMAIN}"

    try:
        parsed = urlparse(config.MAIL_DB_URL)
        conn = await aiomysql.connect(
            host=parsed.hostname or "localhost",
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password,
            db=parsed.path.lstrip("/"),
        )
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT IGNORE INTO mail_users (email, password, domain) VALUES (%s, %s, %s)",
                (email, dovecot_hash, config.MAIL_DOMAIN),
            )
        await conn.commit()
        conn.close()
    except Exception:
        return None

    return encrypt_password(plain_password)
