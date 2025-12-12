from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    """Model for storing dynamic email categories."""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Category identification
    name: str = Field(unique=True, index=True)
    description: Optional[str] = Field(default=None)
    
    # Category metadata
    color: Optional[str] = Field(default=None, max_length=7)  # Hex color code
    icon: Optional[str] = Field(default=None, max_length=50)
    is_system: bool = Field(default=False)  # System categories can't be deleted
    
    # Usage tracking
    email_count: int = Field(default=0)
    
    # Account association (optional - null means global)
    account_id: Optional[int] = Field(default=None, foreign_key="account.id", index=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
