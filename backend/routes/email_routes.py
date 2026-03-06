from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from models import User, EmailTemplate
from schemas import EmailSendRequest, EmailSendResponse, TemplateResponse
from services.email_service import send_email
from services.ai_service import process_template

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


@router.get("/email/template/processed", response_model=TemplateResponse)
async def get_processed_template(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(EmailTemplate).limit(1))
    template = result.scalar_one_or_none()
    if template is None:
        return TemplateResponse(subject="", body="")
    subject, body = await process_template(
        template.subject,
        template.body,
        template.ai_prompt or "",
    )
    return TemplateResponse(subject=subject, body=body)


@router.post("/email/send", response_model=EmailSendResponse)
async def send_email_endpoint(
    payload: EmailSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await send_email(current_user, payload.to, payload.subject, payload.body, db)
    return EmailSendResponse(message="Письмо успешно отправлено")
