from __future__ import annotations

import secrets
from typing import Optional
from urllib.parse import urlparse

import aiomysql
from passlib.hash import sha512_crypt

import config
from utils.crypto import encrypt_password

_DOVECOT_SCHEME = "SHA512-CRYPT"


def _make_dovecot_hash(password: str) -> str:
    return "{" + _DOVECOT_SCHEME + "}" + sha512_crypt.hash(password)


def _parse_mail_db_url(url: str) -> dict:
    parsed = urlparse(url)
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 3306,
        "user": parsed.username,
        "password": parsed.password,
        "db": parsed.path.lstrip("/"),
    }


async def create_mailbox(username: str) -> Optional[str]:
    """
    Creates a virtual mailbox username@MAIL_DOMAIN in the Postfix/Dovecot SQL database.
    Returns encrypted mail password for storage in User.mail_password.
    Returns None if MAIL_DB_URL is not configured (registration proceeds without a mailbox).
    """
    if not config.MAIL_DB_URL:
        return None

    plain_password = secrets.token_urlsafe(20)
    dovecot_hash = _make_dovecot_hash(plain_password)
    email = f"{username}@{config.MAIL_DOMAIN}"

    try:
        params = _parse_mail_db_url(config.MAIL_DB_URL)
        conn = await aiomysql.connect(**params)
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
