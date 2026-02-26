from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import require_admin
from database import get_db
from models import User, EmailTemplate
from schemas import TemplateResponse, TemplateUpdateRequest, MessageResponse

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/template", response_model=TemplateResponse)
async def get_template(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(EmailTemplate).limit(1))
    template = result.scalar_one_or_none()
    if template is None:
        return TemplateResponse(subject="", body="", ai_prompt="")
    return TemplateResponse(subject=template.subject, body=template.body, ai_prompt=template.ai_prompt or "")


@router.put("/template", response_model=MessageResponse)
async def update_template(
    body: TemplateUpdateRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(EmailTemplate).limit(1))
    template = result.scalar_one_or_none()
    if template is None:
        template = EmailTemplate(subject=body.subject, body=body.body, ai_prompt=body.ai_prompt or None)
        db.add(template)
    else:
        template.subject = body.subject
        template.body = body.body
        template.ai_prompt = body.ai_prompt or None
    await db.commit()
    return MessageResponse(message="Шаблон сохранён")
