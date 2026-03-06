from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class LoginRequest(BaseModel):
    login: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    username: str
    email: str
    mail_address: str
    created_at: datetime
    is_admin: bool


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class MessageResponse(BaseModel):
    message: str


class EmailSendRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str


class EmailSendResponse(BaseModel):
    message: str


class TemplateResponse(BaseModel):
    subject: str
    body: str
    ai_prompt: str = ""


class TemplateUpdateRequest(BaseModel):
    subject: str
    body: str
    ai_prompt: str = ""


class EmailMessageItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    direction: str
    from_addr: str
    to_addr: str
    subject: str
    created_at: datetime
    is_read: bool


class EmailMessageDetail(EmailMessageItem):
    body: str


class FetchResult(BaseModel):
    fetched: int
