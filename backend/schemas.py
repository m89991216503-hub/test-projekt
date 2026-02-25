from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class LoginRequest(BaseModel):
    login: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    email: str
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


class TemplateUpdateRequest(BaseModel):
    subject: str
    body: str


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
