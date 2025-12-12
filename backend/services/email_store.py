from datetime import datetime
from typing import Iterable, List, Optional

from sqlmodel import select, or_, col

from db import get_session
from models.email import EmailRecord


def upsert_emails(emails: Iterable[dict]) -> List[EmailRecord]:
    """Insert or update emails, persisting AI fields and interaction flags."""
    records: List[EmailRecord] = []
    with get_session() as session:
        for email in emails:
            gmail_id = email.get("gmail_id")
            existing: Optional[EmailRecord] = None
            if gmail_id:
                stmt = select(EmailRecord).where(EmailRecord.gmail_id == gmail_id)
                existing = session.exec(stmt).first()

            defaults = {
                "subject": email.get("subject", "No Subject"),
                "snippet": email.get("snippet", ""),
                "body_text": email.get("body_text", ""),
                "from_email": email.get("from_email"),
                "account_id": email.get("account_id"),
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


def _escape_like_pattern(pattern: str) -> str:
    """Escape SQL LIKE wildcards in user input to prevent wildcard injection."""
    return pattern.replace("%", "\\%").replace("_", "\\_")


def search_emails(
    query: Optional[str] = None,
    from_email: Optional[str] = None,
    subject: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    is_read: Optional[bool] = None,
    is_starred: Optional[bool] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[EmailRecord]:
    """Search and filter emails with multiple criteria."""
    with get_session() as session:
        stmt = select(EmailRecord)
        
        # Full-text search across subject and body (with wildcard escaping)
        if query:
            escaped_query = _escape_like_pattern(query)
            search_pattern = f"%{escaped_query}%"
            stmt = stmt.where(
                or_(
                    col(EmailRecord.subject).ilike(search_pattern, escape="\\"),
                    col(EmailRecord.body_text).ilike(search_pattern, escape="\\"),
                    col(EmailRecord.snippet).ilike(search_pattern, escape="\\")
                )
            )
        
        # Filter by sender (with wildcard escaping)
        if from_email:
            escaped_email = _escape_like_pattern(from_email)
            stmt = stmt.where(col(EmailRecord.from_email).ilike(f"%{escaped_email}%", escape="\\"))
        
        # Filter by subject (with wildcard escaping)
        if subject:
            escaped_subject = _escape_like_pattern(subject)
            stmt = stmt.where(col(EmailRecord.subject).ilike(f"%{escaped_subject}%", escape="\\"))
        
        # Filter by category
        if category:
            stmt = stmt.where(EmailRecord.category == category)
        
        # Filter by status
        if status:
            stmt = stmt.where(EmailRecord.status == status)
        
        # Filter by read status
        if is_read is not None:
            stmt = stmt.where(EmailRecord.is_read == is_read)
        
        # Filter by starred status
        if is_starred is not None:
            stmt = stmt.where(EmailRecord.is_starred == is_starred)
        
        # Filter by date range
        if date_from:
            stmt = stmt.where(EmailRecord.created_at >= date_from)
        if date_to:
            stmt = stmt.where(EmailRecord.created_at <= date_to)
        
        # Order by most recent first
        stmt = stmt.order_by(EmailRecord.created_at.desc())
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
