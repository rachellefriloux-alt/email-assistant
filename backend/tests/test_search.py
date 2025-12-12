import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Use a throwaway sqlite DB for tests
os.environ["DATABASE_URL"] = "sqlite:///./test_search.db"

from app import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    db_path = Path("test_search.db")
    if db_path.exists():
        db_path.unlink()
    with TestClient(app) as c:
        yield c
    if db_path.exists():
        db_path.unlink()


def test_search_emails_by_query(client):
    """Test searching emails by text query."""
    # First, fetch some sample emails
    resp = client.get("/gmail/fetch", params={"use_sample": True})
    assert resp.status_code == 200
    
    # Search for emails containing specific text
    search_resp = client.get("/gmail/search", params={"query": "invoice"})
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert "emails" in data
    # Should find emails with "invoice" in subject or body
    for email in data["emails"]:
        text = f"{email['subject']} {email.get('body_text', '')} {email.get('snippet', '')}".lower()
        assert "invoice" in text


def test_search_emails_by_sender(client):
    """Test filtering emails by sender."""
    # Fetch sample emails first
    client.get("/gmail/fetch", params={"use_sample": True})
    
    # Search by sender
    search_resp = client.get("/gmail/search", params={"from_email": "example.com"})
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert "emails" in data


def test_search_emails_by_category(client):
    """Test filtering emails by category."""
    # Fetch and categorize an email
    client.post(
        "/categorize/email",
        json={"subject": "Invoice due", "body": "Your payment is pending", "gmail_id": "test-1"},
    )
    
    # Search by category
    search_resp = client.get("/gmail/search", params={"category": "Billing"})
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert "emails" in data
    # Check that results match the category
    for email in data["emails"]:
        assert email["category"] == "Billing"


def test_search_emails_by_status(client):
    """Test filtering emails by status."""
    # Fetch sample emails
    client.get("/gmail/fetch", params={"use_sample": True})
    
    # Search by status
    search_resp = client.get("/gmail/search", params={"status": "keep"})
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert "emails" in data
    for email in data["emails"]:
        assert email["status"] == "keep"


def test_search_emails_pagination(client):
    """Test pagination in search results."""
    # Fetch sample emails
    client.get("/gmail/fetch", params={"use_sample": True})
    
    # Get first page
    resp1 = client.get("/gmail/search", params={"limit": 5, "offset": 0})
    assert resp1.status_code == 200
    page1 = resp1.json()["emails"]
    
    # Get second page
    resp2 = client.get("/gmail/search", params={"limit": 5, "offset": 5})
    assert resp2.status_code == 200
    page2 = resp2.json()["emails"]
    
    # Pages should be different
    if page2:  # Only if there are enough emails
        assert page1[0]["id"] != page2[0]["id"]
