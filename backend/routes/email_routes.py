from fastapi import APIRouter, Depends

from auth import get_current_user
from models import User
from schemas import EmailSendRequest, EmailSendResponse
from services.email_service import send_email
import config

router = APIRouter(prefix="/api")


@router.post("/email/send", response_model=EmailSendResponse)
async def send_email_endpoint(
    payload: EmailSendRequest,
    current_user: User = Depends(get_current_user),
):
    from_addr = config.SMTP_USER or current_user.email
    send_email(from_addr, payload.to, payload.subject, payload.body)
    return EmailSendResponse(message="Письмо успешно отправлено")
