
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.ai_service import analyze_email
from services.email_store import upsert_emails


class EmailPayload(BaseModel):
    subject: str = Field(..., max_length=500)
    body: str = Field(..., max_length=12000)
    gmail_id: Optional[str] = None
    from_email: Optional[str] = None


router = APIRouter()


@router.post("/email")
def categorize(payload: EmailPayload):
    # Extract account_id if available from the email payload
    account_id = payload.dict().get("account_id") if hasattr(payload, "account_id") else None
    
    analysis = analyze_email(payload.subject, payload.body, account_id=account_id, auto_create_category=True)
    record = upsert_emails(
        [
            {
                "gmail_id": payload.gmail_id,
                "subject": payload.subject,
                "snippet": payload.body[:2000],
                "body_text": payload.body,
                "from_email": payload.from_email,
                "category": analysis["category"],
                "sentiment": analysis["sentiment"],
                "urgency": analysis["urgency"],
            }
        ]
    )[0]
    return {"category": analysis["category"], "email": record.model_dump()}
