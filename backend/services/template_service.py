import re
from datetime import datetime
from typing import Dict, List, Optional

from sqlmodel import select

from db import get_session
from models.template import Template


def create_template(
    name: str,
    body_template: str,
    subject_template: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    account_id: Optional[int] = None,
) -> Template:
    """Create a new template."""
    with get_session() as session:
        template = Template(
            name=name,
            body_template=body_template,
            subject_template=subject_template,
            description=description,
            category=category,
            tags=tags,
            account_id=account_id,
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        return template


def get_template(template_id: int) -> Optional[Template]:
    """Get template by ID."""
    with get_session() as session:
        return session.get(Template, template_id)


def list_templates(
    category: Optional[str] = None,
    account_id: Optional[int] = None,
) -> List[Template]:
    """List all templates with optional filtering."""
    with get_session() as session:
        stmt = select(Template)
        if category:
            stmt = stmt.where(Template.category == category)
        if account_id:
            stmt = stmt.where(Template.account_id == account_id)
        stmt = stmt.order_by(Template.usage_count.desc())
        return list(session.exec(stmt))


def update_template(
    template_id: int,
    name: Optional[str] = None,
    body_template: Optional[str] = None,
    subject_template: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
) -> Optional[Template]:
    """Update a template."""
    with get_session() as session:
        template = session.get(Template, template_id)
        if not template:
            return None
        
        if name is not None:
            template.name = name
        if body_template is not None:
            template.body_template = body_template
        if subject_template is not None:
            template.subject_template = subject_template
        if description is not None:
            template.description = description
        if category is not None:
            template.category = category
        if tags is not None:
            template.tags = tags
        
        template.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(template)
        return template


def delete_template(template_id: int) -> bool:
    """Delete a template."""
    with get_session() as session:
        template = session.get(Template, template_id)
        if not template:
            return False
        session.delete(template)
        session.commit()
        return True


def render_template(template_id: int, variables: Dict[str, str]) -> Dict[str, str]:
    """Render a template with variable substitution."""
    template = get_template(template_id)
    if not template:
        raise ValueError(f"Template {template_id} not found")
    
    # Update usage statistics
    with get_session() as session:
        db_template = session.get(Template, template_id)
        if db_template:
            db_template.usage_count += 1
            db_template.last_used = datetime.utcnow()
            session.commit()
    
    # Substitute variables in body
    body = _substitute_variables(template.body_template, variables)
    
    # Substitute variables in subject if present
    subject = None
    if template.subject_template:
        subject = _substitute_variables(template.subject_template, variables)
    
    return {
        "subject": subject,
        "body": body,
    }


def _substitute_variables(text: str, variables: Dict[str, str]) -> str:
    """
    Substitute variables in text.
    Supports {{variable_name}} syntax.
    """
    def replace_var(match):
        var_name = match.group(1).strip()
        return variables.get(var_name, match.group(0))
    
    # Replace {{variable}} patterns
    result = re.sub(r'\{\{(\w+)\}\}', replace_var, text)
    return result


def get_template_variables(template_id: int) -> List[str]:
    """Extract variable names from a template."""
    template = get_template(template_id)
    if not template:
        return []
    
    variables = set()
    
    # Extract from body
    variables.update(re.findall(r'\{\{(\w+)\}\}', template.body_template))
    
    # Extract from subject if present
    if template.subject_template:
        variables.update(re.findall(r'\{\{(\w+)\}\}', template.subject_template))
    
    return sorted(list(variables))
