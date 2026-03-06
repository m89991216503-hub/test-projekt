import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

# DeepSeek AI
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# Mail domain
MAIL_DOMAIN = os.getenv("MAIL_DOMAIN", "school-pro100.ru")

# SMTP for school-pro100.ru (per-user login)
MAIL_SMTP_HOST    = os.getenv("MAIL_SMTP_HOST", "")
MAIL_SMTP_PORT    = int(os.getenv("MAIL_SMTP_PORT", "587"))
MAIL_SMTP_USE_TLS = os.getenv("MAIL_SMTP_USE_TLS", "true").lower() == "true"

# IMAP for school-pro100.ru (per-user login)
MAIL_IMAP_HOST    = os.getenv("MAIL_IMAP_HOST", "")
MAIL_IMAP_PORT    = int(os.getenv("MAIL_IMAP_PORT", "993"))
MAIL_IMAP_USE_SSL = os.getenv("MAIL_IMAP_USE_SSL", "true").lower() == "true"

# Dovecot passwd-file path (used when Dovecot is configured with passwd-file backend)
# Example: /etc/dovecot/dovecot.passwd
DOVECOT_PASSWD_FILE = os.getenv("DOVECOT_PASSWD_FILE", "")

# MySQL database used by Postfix/Dovecot virtual users (used as fallback if no passwd-file)
# Format: mysql+aiomysql://user:password@host/dbname
MAIL_DB_URL = os.getenv("MAIL_DB_URL", "")

# Fernet key for encrypting per-user mail passwords stored in the app DB.
# Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
MAIL_ENCRYPTION_KEY = os.getenv("MAIL_ENCRYPTION_KEY", "")
