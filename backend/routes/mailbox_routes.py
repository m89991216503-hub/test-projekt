from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from models import User, EmailMessage
from schemas import EmailMessageItem, EmailMessageDetail, FetchResult
from services.imap_service import fetch_inbox

router = APIRouter(prefix="/api/mailbox", tags=["mailbox"])


@router.get("/inbox", response_model=list[EmailMessageItem])
async def get_inbox(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Collect subjects from user's own sent emails (strip leading "Re: " for normalization)
    sent_result = await db.execute(
        select(EmailMessage.subject)
        .where(EmailMessage.user_id == current_user.id, EmailMessage.direction == "sent")
    )
    re_prefix = "Re: "
    sent_normalized = {row[0].removeprefix(re_prefix).strip().lower() for row in sent_result.all()}

    if not sent_normalized:
        return []

    # Fetch all received messages and filter by matching subject
    recv_result = await db.execute(
        select(EmailMessage)
        .where(EmailMessage.direction == "recv")
        .order_by(EmailMessage.created_at.desc())
    )
    all_recv = recv_result.scalars().all()

    return [
        m for m in all_recv
        if m.subject.removeprefix(re_prefix).strip().lower() in sent_normalized
    ]


@router.get("/sent", response_model=list[EmailMessageItem])
async def get_sent(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmailMessage)
        .where(EmailMessage.user_id == current_user.id, EmailMessage.direction == "sent")
        .order_by(EmailMessage.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{msg_id}", response_model=EmailMessageDetail)
async def get_message(
    msg_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(EmailMessage).where(EmailMessage.id == msg_id))
    msg = result.scalar_one_or_none()
    if msg is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    if msg.direction == "sent" and msg.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if msg.direction == "recv" and not msg.is_read:
        msg.is_read = True
        db.add(msg)
        await db.commit()
    return msg


@router.post("/fetch", response_model=FetchResult)
async def fetch_emails(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    fetched = await fetch_inbox(db, users, fallback_user_id=current_user.id)
    return FetchResult(fetched=fetched)
