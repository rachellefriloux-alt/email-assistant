from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.category_service import (
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)


router = APIRouter()


class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, max_length=7, description="Hex color code (e.g., #FF5733)")
    icon: Optional[str] = Field(None, max_length=50)
    account_id: Optional[int] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)


@router.post("/")
def create_new_category(payload: CategoryCreate):
    """Create a new category."""
    category = create_category(
        name=payload.name,
        description=payload.description,
        color=payload.color,
        icon=payload.icon,
        account_id=payload.account_id,
    )
    return {"category": category.model_dump()}


@router.get("/")
def list_all_categories(
    account_id: Optional[int] = None,
    include_global: bool = True,
):
    """List all categories."""
    categories = list_categories(account_id=account_id, include_global=include_global)
    return {"categories": [cat.model_dump() for cat in categories]}


@router.get("/{category_id}")
def get_category_details(category_id: int):
    """Get category details by ID."""
    category = get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"category": category.model_dump()}


@router.patch("/{category_id}")
def update_existing_category(category_id: int, payload: CategoryUpdate):
    """Update a category."""
    category = update_category(
        category_id=category_id,
        name=payload.name,
        description=payload.description,
        color=payload.color,
        icon=payload.icon,
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"category": category.model_dump()}


@router.delete("/{category_id}")
def remove_category(category_id: int):
    """Delete a category (only non-system categories)."""
    success = delete_category(category_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Category not found or cannot delete system category"
        )
    return {"deleted": True}
