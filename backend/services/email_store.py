from datetime import datetime
from typing import Iterable, List, Optional

from sqlmodel import select

from db import get_session
from models.email import EmailRecord


def upsert_emails(emails: Iterable[dict]) -> List[EmailRecord]:
    """Insert or update emails, persisting AI fields and interaction flags."""
    records: List[EmailRecord] = []
    with get_session() as session:
        for email in emails:
            gmail_id = email.get("gmail_id")
            stmt = select(EmailRecord).where(EmailRecord.gmail_id == gmail_id) if gmail_id else None
            existing: Optional[EmailRecord] = session.exec(stmt).first() if stmt else None

            defaults = {
                "subject": email.get("subject", "No Subject"),
                "snippet": email.get("snippet", ""),
                "body_text": email.get("body_text", ""),
                "from_email": email.get("from_email"),
                "category": email.get("category", "Unlabeled"),
                "sentiment": email.get("sentiment", "Neutral"),
                "urgency": email.get("urgency", "Normal"),
                "status": email.get("status", "keep"),
                "is_read": email.get("is_read", False),
                "is_starred": email.get("is_starred", False),
            }

            if existing:
                for field, value in defaults.items():
                    setattr(existing, field, value if value is not None else getattr(existing, field))
                existing.updated_at = datetime.utcnow()
                records.append(existing)
            else:
                rec = EmailRecord(
                    gmail_id=gmail_id,
                    **defaults,
                )
                session.add(rec)
                records.append(rec)
        session.commit()
        for rec in records:
            session.refresh(rec)
    return records


def list_emails(
    status: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[EmailRecord]:
    with get_session() as session:
        stmt = select(EmailRecord)
        if status:
            stmt = stmt.where(EmailRecord.status == status)
        if category:
            stmt = stmt.where(EmailRecord.category == category)
        stmt = stmt.offset(offset).limit(limit)
        return list(session.exec(stmt))


def mark_status(ids: List[int], status: str) -> int:
    with get_session() as session:
        stmt = select(EmailRecord).where(EmailRecord.id.in_(ids))
        records = list(session.exec(stmt))
        for rec in records:
            rec.status = status
            rec.updated_at = datetime.utcnow()
        session.commit()
        return len(records)


def delete_by_gmail_ids(gmail_ids: List[str]) -> int:
    with get_session() as session:
        stmt = select(EmailRecord).where(EmailRecord.gmail_id.in_(gmail_ids))
        records = list(session.exec(stmt))
        for rec in records:
            rec.status = "deleted"
            rec.updated_at = datetime.utcnow()
        session.commit()
        return len(records)
