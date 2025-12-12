import logging
from datetime import datetime
from typing import List, Optional

from sqlmodel import select

from db import get_session
from models.category import Category

log = logging.getLogger(__name__)

# Default system categories
DEFAULT_CATEGORIES = [
    {"name": "Billing", "description": "Invoices, payments, receipts", "is_system": True, "color": "#4CAF50"},
    {"name": "Account Info", "description": "Account settings, security", "is_system": True, "color": "#2196F3"},
    {"name": "Work Update", "description": "Meetings, projects, reports", "is_system": True, "color": "#FF9800"},
    {"name": "Promotion", "description": "Sales, offers, deals", "is_system": True, "color": "#9C27B0"},
    {"name": "Spam", "description": "Unwanted emails", "is_system": True, "color": "#F44336"},
    {"name": "Personal", "description": "Personal correspondence", "is_system": True, "color": "#00BCD4"},
]


def initialize_default_categories():
    """Initialize default system categories if they don't exist."""
    with get_session() as session:
        for cat_data in DEFAULT_CATEGORIES:
            stmt = select(Category).where(Category.name == cat_data["name"], Category.account_id.is_(None))
            existing = session.exec(stmt).first()
            if not existing:
                category = Category(**cat_data)
                session.add(category)
        session.commit()
        log.info("Default categories initialized")


def create_category(
    name: str,
    description: Optional[str] = None,
    color: Optional[str] = None,
    icon: Optional[str] = None,
    account_id: Optional[int] = None,
) -> Category:
    """Create a new category."""
    with get_session() as session:
        # Check if category already exists
        stmt = select(Category).where(Category.name == name)
        if account_id:
            stmt = stmt.where(Category.account_id == account_id)
        else:
            stmt = stmt.where(Category.account_id.is_(None))
        
        existing = session.exec(stmt).first()
        if existing:
            return existing
        
        category = Category(
            name=name,
            description=description,
            color=color,
            icon=icon,
            account_id=account_id,
            is_system=False,
        )
        session.add(category)
        session.commit()
        session.refresh(category)
        log.info(f"Created new category: {name}")
        return category


def get_category(category_id: int) -> Optional[Category]:
    """Get category by ID."""
    with get_session() as session:
        return session.get(Category, category_id)


def get_category_by_name(name: str, account_id: Optional[int] = None) -> Optional[Category]:
    """Get category by name."""
    with get_session() as session:
        stmt = select(Category).where(Category.name == name)
        if account_id:
            stmt = stmt.where(Category.account_id == account_id)
        else:
            stmt = stmt.where(Category.account_id.is_(None))
        return session.exec(stmt).first()


def list_categories(account_id: Optional[int] = None, include_global: bool = True) -> List[Category]:
    """List all categories."""
    with get_session() as session:
        stmt = select(Category)
        
        if account_id and include_global:
            # Include both account-specific and global categories
            stmt = stmt.where(
                (Category.account_id == account_id) | (Category.account_id.is_(None))
            )
        elif account_id:
            # Only account-specific
            stmt = stmt.where(Category.account_id == account_id)
        else:
            # Only global
            stmt = stmt.where(Category.account_id.is_(None))
        
        stmt = stmt.order_by(Category.is_system.desc(), Category.email_count.desc())
        return list(session.exec(stmt))


def update_category(
    category_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    color: Optional[str] = None,
    icon: Optional[str] = None,
) -> Optional[Category]:
    """Update a category."""
    with get_session() as session:
        category = session.get(Category, category_id)
        if not category:
            return None
        
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        if color is not None:
            category.color = color
        if icon is not None:
            category.icon = icon
        
        category.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(category)
        return category


def delete_category(category_id: int) -> bool:
    """Delete a category (only non-system categories)."""
    with get_session() as session:
        category = session.get(Category, category_id)
        if not category or category.is_system:
            return False
        session.delete(category)
        session.commit()
        return True


def increment_category_count(category_name: str, account_id: Optional[int] = None):
    """Increment the email count for a category."""
    with get_session() as session:
        stmt = select(Category).where(Category.name == category_name)
        if account_id:
            stmt = stmt.where(Category.account_id == account_id)
        else:
            stmt = stmt.where(Category.account_id.is_(None))
        
        category = session.exec(stmt).first()
        if category:
            category.email_count += 1
            category.updated_at = datetime.utcnow()
            session.commit()


def auto_create_category_if_needed(category_name: str, account_id: Optional[int] = None) -> str:
    """
    Auto-create a category if it doesn't exist.
    Returns the category name (normalized).
    """
    if not category_name or category_name == "Unlabeled":
        return "Unlabeled"
    
    # Check if category exists
    existing = get_category_by_name(category_name, account_id)
    if existing:
        return existing.name
    
    # Create new category dynamically
    try:
        new_category = create_category(
            name=category_name,
            description=f"Auto-created category for {category_name} emails",
            account_id=account_id,
        )
        log.info(f"Auto-created category: {category_name}")
        return new_category.name
    except Exception as e:
        log.error(f"Failed to auto-create category {category_name}: {e}")
        return "Unlabeled"
