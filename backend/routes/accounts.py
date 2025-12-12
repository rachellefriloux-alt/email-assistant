from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from services.account_service import (
    create_account,
    delete_account,
    get_account,
    get_account_by_email,
    list_accounts,
    update_account_settings,
    update_account_tokens,
)


router = APIRouter()


class AccountCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    fetch_enabled: Optional[bool] = None
    fetch_interval_minutes: Optional[int] = Field(None, ge=1, le=1440)


class TokenUpdate(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None


@router.post("/")
def create_new_account(payload: AccountCreate):
    """Create a new Gmail account."""
    existing = get_account_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Account with this email already exists")
    
    account = create_account(
        email=payload.email,
        name=payload.name,
        access_token=payload.access_token,
        refresh_token=payload.refresh_token,
        token_expiry=payload.token_expiry,
    )
    return {"account": account.dict()}


@router.get("/")
def list_all_accounts(active_only: bool = False):
    """List all accounts."""
    accounts = list_accounts(active_only=active_only)
    return {"accounts": [acc.dict() for acc in accounts]}


@router.get("/{account_id}")
def get_account_details(account_id: int):
    """Get account details by ID."""
    account = get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account": account.dict()}


@router.patch("/{account_id}")
def update_account(account_id: int, payload: AccountUpdate):
    """Update account settings."""
    account = update_account_settings(
        account_id=account_id,
        name=payload.name,
        is_active=payload.is_active,
        fetch_enabled=payload.fetch_enabled,
        fetch_interval_minutes=payload.fetch_interval_minutes,
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account": account.dict()}


@router.patch("/{account_id}/tokens")
def update_tokens(account_id: int, payload: TokenUpdate):
    """Update account OAuth tokens."""
    account = update_account_tokens(
        account_id=account_id,
        access_token=payload.access_token,
        refresh_token=payload.refresh_token,
        token_expiry=payload.token_expiry,
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account": account.dict()}


@router.delete("/{account_id}")
def remove_account(account_id: int):
    """Delete an account."""
    success = delete_account(account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"deleted": True}
