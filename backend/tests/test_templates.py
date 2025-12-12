import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Use a throwaway sqlite DB for tests
os.environ["DATABASE_URL"] = "sqlite:///./test_templates.db"

from app import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    db_path = Path("test_templates.db")
    if db_path.exists():
        db_path.unlink()
    with TestClient(app) as c:
        yield c
    if db_path.exists():
        db_path.unlink()


def test_create_template(client):
    """Test creating a new template."""
    resp = client.post(
        "/templates/",
        json={
            "name": "Welcome Email",
            "body_template": "Hello {{name}}, welcome to our service!",
            "subject_template": "Welcome {{name}}!",
            "description": "Welcome email for new users",
            "category": "Onboarding",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "template" in data
    assert data["template"]["name"] == "Welcome Email"
    assert "{{name}}" in data["template"]["body_template"]


def test_list_templates(client):
    """Test listing all templates."""
    # Create a couple of templates
    client.post(
        "/templates/",
        json={"name": "Template 1", "body_template": "Body 1"},
    )
    client.post(
        "/templates/",
        json={"name": "Template 2", "body_template": "Body 2"},
    )
    
    # List all templates
    resp = client.get("/templates/")
    assert resp.status_code == 200
    data = resp.json()
    assert "templates" in data
    assert len(data["templates"]) >= 2


def test_get_template_details(client):
    """Test getting template details."""
    # Create template
    create_resp = client.post(
        "/templates/",
        json={
            "name": "Test Template",
            "body_template": "Test body",
            "description": "Test description",
        },
    )
    template_id = create_resp.json()["template"]["id"]
    
    # Get details
    resp = client.get(f"/templates/{template_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["template"]["name"] == "Test Template"
    assert data["template"]["description"] == "Test description"


def test_update_template(client):
    """Test updating a template."""
    # Create template
    create_resp = client.post(
        "/templates/",
        json={"name": "Original Name", "body_template": "Original body"},
    )
    template_id = create_resp.json()["template"]["id"]
    
    # Update template
    resp = client.patch(
        f"/templates/{template_id}",
        json={
            "name": "Updated Name",
            "body_template": "Updated body",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["template"]["name"] == "Updated Name"
    assert data["template"]["body_template"] == "Updated body"


def test_delete_template(client):
    """Test deleting a template."""
    # Create template
    create_resp = client.post(
        "/templates/",
        json={"name": "To Delete", "body_template": "Delete me"},
    )
    template_id = create_resp.json()["template"]["id"]
    
    # Delete template
    resp = client.delete(f"/templates/{template_id}")
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True
    
    # Verify template is deleted
    get_resp = client.get(f"/templates/{template_id}")
    assert get_resp.status_code == 404


def test_render_template_with_variables(client):
    """Test rendering a template with variable substitution."""
    # Create template with variables
    create_resp = client.post(
        "/templates/",
        json={
            "name": "Greeting",
            "body_template": "Hello {{name}}, your order {{order_id}} is ready!",
            "subject_template": "Order {{order_id}} Update",
        },
    )
    template_id = create_resp.json()["template"]["id"]
    
    # Render template
    resp = client.post(
        "/templates/render",
        json={
            "template_id": template_id,
            "variables": {
                "name": "John",
                "order_id": "12345",
            },
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "Hello John, your order 12345 is ready!" == data["body"]
    assert "Order 12345 Update" == data["subject"]


def test_get_template_variables(client):
    """Test extracting variables from a template."""
    # Create template with variables
    create_resp = client.post(
        "/templates/",
        json={
            "name": "Variable Test",
            "body_template": "Hello {{name}}, your {{item}} is {{status}}.",
            "subject_template": "{{status}} notification",
        },
    )
    template_id = create_resp.json()["template"]["id"]
    
    # Get variables
    resp = client.get(f"/templates/{template_id}/variables")
    assert resp.status_code == 200
    data = resp.json()
    assert "variables" in data
    variables = data["variables"]
    assert "name" in variables
    assert "item" in variables
    assert "status" in variables


def test_filter_templates_by_category(client):
    """Test filtering templates by category."""
    # Create templates with different categories
    client.post(
        "/templates/",
        json={"name": "Billing Template", "body_template": "Body", "category": "Billing"},
    )
    client.post(
        "/templates/",
        json={"name": "Support Template", "body_template": "Body", "category": "Support"},
    )
    
    # Filter by category
    resp = client.get("/templates/", params={"category": "Billing"})
    assert resp.status_code == 200
    data = resp.json()
    templates = data["templates"]
    
    # Check all returned templates have the correct category
    for template in templates:
        if template["category"] is not None:
            assert template["category"] == "Billing"


def test_template_usage_tracking(client):
    """Test that template usage is tracked."""
    # Create template
    create_resp = client.post(
        "/templates/",
        json={"name": "Usage Test", "body_template": "Test {{var}}"},
    )
    template_id = create_resp.json()["template"]["id"]
    
    # Get initial usage count
    initial_resp = client.get(f"/templates/{template_id}")
    initial_count = initial_resp.json()["template"]["usage_count"]
    
    # Render template
    client.post(
        "/templates/render",
        json={"template_id": template_id, "variables": {"var": "value"}},
    )
    
    # Check usage count increased
    final_resp = client.get(f"/templates/{template_id}")
    final_count = final_resp.json()["template"]["usage_count"]
    assert final_count == initial_count + 1
