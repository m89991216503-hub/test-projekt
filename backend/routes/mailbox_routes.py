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
    result = await db.execute(
        select(EmailMessage)
        .where(EmailMessage.user_id == current_user.id, EmailMessage.direction == "recv")
        .order_by(EmailMessage.created_at.desc())
    )
    return result.scalars().all()


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
    if msg.user_id != current_user.id:
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
    fetched = await fetch_inbox(db, users)
    return FetchResult(fetched=fetched)
