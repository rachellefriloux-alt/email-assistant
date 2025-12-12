from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class EmailThread(SQLModel, table=True):
    """Model for grouping related emails into conversation threads."""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Thread identification
    thread_id: str = Field(unique=True, index=True)  # Gmail thread ID or generated ID
    subject: str = Field(index=True)
    
    # Thread metadata
    message_count: int = Field(default=0)
    participant_count: int = Field(default=0)
    participants: Optional[str] = Field(default=None)  # Comma-separated email addresses
    
    # Thread status
    has_unread: bool = Field(default=False)
    is_archived: bool = Field(default=False)
    
    # Timestamps
    first_message_at: Optional[datetime] = Field(default=None)
    last_message_at: Optional[datetime] = Field(default=None)
    
    # Account association
    account_id: Optional[int] = Field(default=None, foreign_key="account.id", index=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
