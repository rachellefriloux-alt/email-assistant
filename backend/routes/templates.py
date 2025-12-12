from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.template_service import (
    create_template,
    delete_template,
    get_template,
    get_template_variables,
    list_templates,
    render_template,
    update_template,
)


router = APIRouter()


class TemplateCreate(BaseModel):
    name: str = Field(..., max_length=200)
    body_template: str = Field(..., max_length=10000)
    subject_template: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)
    account_id: Optional[int] = None


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    body_template: Optional[str] = Field(None, max_length=10000)
    subject_template: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)


class TemplateRender(BaseModel):
    template_id: int
    variables: Dict[str, str] = Field(default_factory=dict)


@router.post("/")
def create_new_template(payload: TemplateCreate):
    """Create a new reply template."""
    template = create_template(
        name=payload.name,
        body_template=payload.body_template,
        subject_template=payload.subject_template,
        description=payload.description,
        category=payload.category,
        tags=payload.tags,
        account_id=payload.account_id,
    )
    return {"template": template.model_dump()}


@router.get("/")
def list_all_templates(
    category: Optional[str] = None,
    account_id: Optional[int] = None,
):
    """List all templates with optional filtering."""
    templates = list_templates(category=category, account_id=account_id)
    return {"templates": [t.model_dump() for t in templates]}


@router.get("/{template_id}")
def get_template_details(template_id: int):
    """Get template details by ID."""
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"template": template.model_dump()}


@router.get("/{template_id}/variables")
def get_variables(template_id: int):
    """Get list of variables used in a template."""
    variables = get_template_variables(template_id)
    return {"variables": variables}


@router.patch("/{template_id}")
def update_existing_template(template_id: int, payload: TemplateUpdate):
    """Update a template."""
    template = update_template(
        template_id=template_id,
        name=payload.name,
        body_template=payload.body_template,
        subject_template=payload.subject_template,
        description=payload.description,
        category=payload.category,
        tags=payload.tags,
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"template": template.model_dump()}


@router.delete("/{template_id}")
def remove_template(template_id: int):
    """Delete a template."""
    success = delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"deleted": True}


@router.post("/render")
def render_template_with_variables(payload: TemplateRender):
    """Render a template with variable substitution."""
    try:
        result = render_template(payload.template_id, payload.variables)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
