from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class EmailRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    gmail_id: Optional[str] = Field(default=None, index=True)
    account_id: Optional[int] = Field(default=None, foreign_key="account.id", index=True)
    thread_id: Optional[str] = Field(default=None, index=True)  # For email threading
    
    # Core Content
    subject: str
    snippet: Optional[str] = Field(default="", max_length=2000)
    body_text: Optional[str] = Field(default="") # Added full body storage
    from_email: Optional[str] = Field(default=None, index=True)
    to_email: Optional[str] = Field(default=None)  # Recipients
    has_attachments: bool = Field(default=False)  # Attachment indicator
    
    # AI Analysis Fields
    category: Optional[str] = Field(default="Unlabeled")
    sentiment: Optional[str] = Field(default="Neutral") # New: Positive/Negative/Neutral
    urgency: Optional[str] = Field(default="Normal")    # New: High/Normal
    
    # User Interaction
    status: str = Field(default="keep")  # keep | delete_review | deleted | archived
    is_read: bool = Field(default=False)
    is_starred: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
