from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from models import User, EmailTemplate
from schemas import EmailSendRequest, EmailSendResponse, TemplateResponse
from services.email_service import send_email
import config

router = APIRouter(prefix="/api")


@router.get("/email/template", response_model=TemplateResponse)
async def get_email_template(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(EmailTemplate).limit(1))
    template = result.scalar_one_or_none()
    if template is None:
        return TemplateResponse(subject="", body="")
    return TemplateResponse(subject=template.subject, body=template.body)


@router.post("/email/send", response_model=EmailSendResponse)
async def send_email_endpoint(
    payload: EmailSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from_addr = config.SMTP_USER or current_user.email
    await send_email(from_addr, payload.to, payload.subject, payload.body, current_user.id, db)
    return EmailSendResponse(message="Письмо успешно отправлено")
