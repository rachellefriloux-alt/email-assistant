from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Template(SQLModel, table=True):
    """Model for storing reply templates and macros."""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Template identification
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    
    # Template content
    subject_template: Optional[str] = Field(default=None)
    body_template: str
    
    # Template metadata
    category: Optional[str] = Field(default=None, index=True)
    tags: Optional[str] = Field(default=None)  # Comma-separated tags
    
    # Usage tracking
    usage_count: int = Field(default=0)
    last_used: Optional[datetime] = Field(default=None)
    
    # Account association (optional)
    account_id: Optional[int] = Field(default=None, foreign_key="account.id", index=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
