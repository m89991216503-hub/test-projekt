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

# Fastpanel keeps delivery routing in a separate file from the Dovecot auth file.
# When EXIM_PASSWD_FILE is set alongside DOVECOT_PASSWD_FILE, new users are written
# to both files (Dovecot format for auth, Exim4 format for routing).
_DOVECOT_ENTRY_FMT = "{email}:{hash}:{uid}:{gid}::{home}::\n"
_EXIM_ENTRY_FMT    = "{email}:{hash}:{uid}:{gid}:{home}::\n"


def _make_dovecot_hash(password: str) -> str:
    return "{" + _DOVECOT_SCHEME + "}" + sha512_crypt.hash(password)


async def create_mailbox(username: str) -> Optional[str]:
    """
    Creates a virtual mailbox username@MAIL_DOMAIN.

    Backends (checked in order):
      1. DOVECOT_PASSWD_FILE — appends to Dovecot passwd-file and creates mail directory.
         If EXIM_PASSWD_FILE is also set (Fastpanel setup), also writes the Exim4 routing entry.
      2. MAIL_DB_URL — inserts into Postfix/Dovecot MySQL virtual_users table.

    Returns encrypted mail password for storage in User.mail_password.
    Returns None if neither backend is configured (registration proceeds without a mailbox).
    """
    if config.DOVECOT_PASSWD_FILE:
        return await _create_mailbox_passwdfile(username)

    if config.MAIL_DB_URL:
        return await _create_mailbox_mysql(username)

    return None


async def _create_mailbox_passwdfile(username: str) -> Optional[str]:
    email = f"{username}@{config.MAIL_DOMAIN}"
    plain_password = secrets.token_urlsafe(20)
    dovecot_hash = _make_dovecot_hash(plain_password)
    mail_home = f"/var/mail/vhosts/{config.MAIL_DOMAIN}/{username}"
    dovecot_passwd_file = config.DOVECOT_PASSWD_FILE
    exim_passwd_file = config.EXIM_PASSWD_FILE  # may be empty string

    try:
        # Skip if user already exists in Dovecot passwd-file
        if os.path.exists(dovecot_passwd_file):
            with open(dovecot_passwd_file, "r") as f:
                for line in f:
                    if line.startswith(email + ":"):
                        return None

        # Write Dovecot auth entry:  email:hash:uid:gid::home::
        dovecot_entry = _DOVECOT_ENTRY_FMT.format(
            email=email, hash=dovecot_hash, uid=_MAIL_UID, gid=_MAIL_GID, home=mail_home
        )
        with open(dovecot_passwd_file, "a") as f:
            f.write(dovecot_entry)

        # Write Exim4 routing entry (Fastpanel): email:hash:uid:gid:home::
        if exim_passwd_file and os.path.exists(exim_passwd_file):
            exim_entry = _EXIM_ENTRY_FMT.format(
                email=email, hash=dovecot_hash, uid=_MAIL_UID, gid=_MAIL_GID, home=mail_home
            )
            with open(exim_passwd_file, "a") as f:
                f.write(exim_entry)

        # Create mailbox directory
        os.makedirs(mail_home, mode=0o770, exist_ok=True)
        os.chown(mail_home, _MAIL_UID, _MAIL_GID)

        # Reload Dovecot to pick up new user
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
