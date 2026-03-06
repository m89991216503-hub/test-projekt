from cryptography.fernet import Fernet

import config


def _fernet() -> Fernet:
    if not config.MAIL_ENCRYPTION_KEY:
        raise RuntimeError("MAIL_ENCRYPTION_KEY is not configured")
    return Fernet(config.MAIL_ENCRYPTION_KEY.encode())


def encrypt_password(plain: str) -> str:
    return _fernet().encrypt(plain.encode()).decode()


def decrypt_password(token: str) -> str:
    return _fernet().decrypt(token.encode()).decode()
