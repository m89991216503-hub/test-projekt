from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import verify_password, hash_password, create_access_token
from database import get_db
from models import User
from schemas import LoginRequest, RegisterRequest, TokenResponse
from services.mailbox_service import create_mailbox

router = APIRouter(prefix="/api", tags=["auth"])

_USERNAME_RE = re.compile(r"^[a-z0-9._-]{3,30}$")


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    if "@" in body.login:
        result = await db.execute(select(User).where(User.email == body.login))
    else:
        result = await db.execute(select(User).where(User.username == body.login))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login or password")
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if not _USERNAME_RE.match(body.username):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username must be 3–30 characters: lowercase letters, digits, dot, hyphen, underscore",
        )

    if len(body.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 6 characters",
        )

    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    result = await db.execute(select(User).where(User.username == body.username))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    mail_password = await create_mailbox(body.username)

    user = User(
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
        mail_password=mail_password,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))
