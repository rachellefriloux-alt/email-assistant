from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Account(SQLModel, table=True):
    """Model for storing multiple Gmail account credentials."""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Account identification
    email: str = Field(unique=True, index=True)
    name: Optional[str] = Field(default=None)
    
    # OAuth tokens (encrypted in production)
    access_token: Optional[str] = Field(default=None)
    refresh_token: Optional[str] = Field(default=None)
    token_expiry: Optional[datetime] = Field(default=None)
    
    # Settings
    is_active: bool = Field(default=True)
    fetch_enabled: bool = Field(default=True)
    fetch_interval_minutes: int = Field(default=15)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
