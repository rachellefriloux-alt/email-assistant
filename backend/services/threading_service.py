import logging
import re
from datetime import datetime
from typing import List, Optional

from sqlmodel import select

from db import get_session
from models.email import EmailRecord
from models.thread import EmailThread

log = logging.getLogger(__name__)


def normalize_subject(subject: str) -> str:
    """Normalize email subject for threading by removing Re:, Fwd:, etc."""
    # Remove common prefixes
    subject = re.sub(r'^(re|fwd|fw):\s*', '', subject, flags=re.IGNORECASE)
    # Remove extra whitespace
    subject = ' '.join(subject.split())
    return subject.lower()


def get_or_create_thread(
    thread_id: Optional[str],
    subject: str,
    from_email: str,
    to_email: Optional[str],
    message_date: Optional[datetime],
    account_id: Optional[int] = None,
) -> EmailThread:
    """Get existing thread or create a new one."""
    with get_session() as session:
        # Try to find existing thread by thread_id
        if thread_id:
            stmt = select(EmailThread).where(EmailThread.thread_id == thread_id)
            existing = session.exec(stmt).first()
            if existing:
                return existing
        
        # Try to find by normalized subject
        normalized_subject = normalize_subject(subject)
        stmt = select(EmailThread).where(
            EmailThread.subject == normalized_subject
        )
        if account_id:
            stmt = stmt.where(EmailThread.account_id == account_id)
        
        existing = session.exec(stmt).first()
        if existing:
            return existing
        
        # Create new thread
        participants = set()
        if from_email:
            participants.add(from_email)
        if to_email:
            # Handle multiple recipients
            for email in to_email.split(','):
                participants.add(email.strip())
        
        thread = EmailThread(
            thread_id=thread_id or f"thread_{normalized_subject[:50]}_{datetime.utcnow().timestamp()}",
            subject=normalized_subject,
            message_count=0,
            participant_count=len(participants),
            participants=','.join(participants),
            first_message_at=message_date,
            last_message_at=message_date,
            account_id=account_id,
        )
        session.add(thread)
        session.commit()
        session.refresh(thread)
        log.info(f"Created new thread: {thread.thread_id}")
        return thread


def update_thread_stats(thread_id: str):
    """Update thread statistics based on associated emails."""
    with get_session() as session:
        # Get thread
        stmt = select(EmailThread).where(EmailThread.thread_id == thread_id)
        thread = session.exec(stmt).first()
        if not thread:
            return
        
        # Get all emails in thread
        email_stmt = select(EmailRecord).where(EmailRecord.thread_id == thread_id)
        emails = list(session.exec(email_stmt))
        
        if not emails:
            return
        
        # Update stats
        thread.message_count = len(emails)
        thread.has_unread = any(not email.is_read for email in emails)
        
        # Update timestamps
        dates = [email.created_at for email in emails]
        thread.first_message_at = min(dates)
        thread.last_message_at = max(dates)
        
        # Update participants
        participants = set()
        for email in emails:
            if email.from_email:
                participants.add(email.from_email)
            if email.to_email:
                for addr in email.to_email.split(','):
                    participants.add(addr.strip())
        
        thread.participant_count = len(participants)
        thread.participants = ','.join(participants)
        thread.updated_at = datetime.utcnow()
        
        session.commit()


def get_thread_emails(thread_id: str, limit: int = 100) -> List[EmailRecord]:
    """Get all emails in a thread, ordered by date."""
    with get_session() as session:
        stmt = select(EmailRecord).where(EmailRecord.thread_id == thread_id)
        stmt = stmt.order_by(EmailRecord.created_at.asc()).limit(limit)
        return list(session.exec(stmt))


def list_threads(
    account_id: Optional[int] = None,
    unread_only: bool = False,
    archived_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> List[EmailThread]:
    """List email threads with filters."""
    with get_session() as session:
        stmt = select(EmailThread)
        
        if account_id:
            stmt = stmt.where(EmailThread.account_id == account_id)
        
        if unread_only:
            stmt = stmt.where(EmailThread.has_unread.is_(True))
        
        if archived_only:
            stmt = stmt.where(EmailThread.is_archived.is_(True))
        else:
            stmt = stmt.where(EmailThread.is_archived.is_(False))
        
        stmt = stmt.order_by(EmailThread.last_message_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        
        return list(session.exec(stmt))


def archive_thread(thread_id: str) -> bool:
    """Archive a thread."""
    with get_session() as session:
        stmt = select(EmailThread).where(EmailThread.thread_id == thread_id)
        thread = session.exec(stmt).first()
        if not thread:
            return False
        
        thread.is_archived = True
        thread.updated_at = datetime.utcnow()
        session.commit()
        return True


def unarchive_thread(thread_id: str) -> bool:
    """Unarchive a thread."""
    with get_session() as session:
        stmt = select(EmailThread).where(EmailThread.thread_id == thread_id)
        thread = session.exec(stmt).first()
        if not thread:
            return False
        
        thread.is_archived = False
        thread.updated_at = datetime.utcnow()
        session.commit()
        return True
