from datetime import datetime
from typing import List, Optional

from sqlmodel import select

from db import get_session
from models.account import Account


def create_account(
    email: str,
    name: Optional[str] = None,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
    token_expiry: Optional[datetime] = None,
) -> Account:
    """Create a new account."""
    with get_session() as session:
        account = Account(
            email=email,
            name=name,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expiry=token_expiry,
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        return account


def get_account(account_id: int) -> Optional[Account]:
    """Get account by ID."""
    with get_session() as session:
        return session.get(Account, account_id)


def get_account_by_email(email: str) -> Optional[Account]:
    """Get account by email address."""
    with get_session() as session:
        stmt = select(Account).where(Account.email == email)
        return session.exec(stmt).first()


def list_accounts(active_only: bool = False) -> List[Account]:
    """List all accounts."""
    with get_session() as session:
        stmt = select(Account)
        if active_only:
            stmt = stmt.where(Account.is_active == True)
        return list(session.exec(stmt))


def update_account_tokens(
    account_id: int,
    access_token: str,
    refresh_token: Optional[str] = None,
    token_expiry: Optional[datetime] = None,
) -> Optional[Account]:
    """Update account OAuth tokens."""
    with get_session() as session:
        account = session.get(Account, account_id)
        if not account:
            return None
        account.access_token = access_token
        if refresh_token:
            account.refresh_token = refresh_token
        if token_expiry:
            account.token_expiry = token_expiry
        account.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(account)
        return account


def update_account_settings(
    account_id: int,
    is_active: Optional[bool] = None,
    fetch_enabled: Optional[bool] = None,
    fetch_interval_minutes: Optional[int] = None,
    name: Optional[str] = None,
) -> Optional[Account]:
    """Update account settings."""
    with get_session() as session:
        account = session.get(Account, account_id)
        if not account:
            return None
        if is_active is not None:
            account.is_active = is_active
        if fetch_enabled is not None:
            account.fetch_enabled = fetch_enabled
        if fetch_interval_minutes is not None:
            account.fetch_interval_minutes = fetch_interval_minutes
        if name is not None:
            account.name = name
        account.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(account)
        return account


def delete_account(account_id: int) -> bool:
    """Delete an account."""
    with get_session() as session:
        account = session.get(Account, account_id)
        if not account:
            return False
        session.delete(account)
        session.commit()
        return True
