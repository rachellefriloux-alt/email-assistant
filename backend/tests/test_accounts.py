import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Use a throwaway sqlite DB for tests
os.environ["DATABASE_URL"] = "sqlite:///./test_accounts.db"

from app import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    db_path = Path("test_accounts.db")
    if db_path.exists():
        db_path.unlink()
    with TestClient(app) as c:
        yield c
    if db_path.exists():
        db_path.unlink()


def test_create_account(client):
    """Test creating a new account."""
    resp = client.post(
        "/accounts/",
        json={
            "email": "test@example.com",
            "name": "Test Account",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "account" in data
    assert data["account"]["email"] == "test@example.com"
    assert data["account"]["name"] == "Test Account"
    assert data["account"]["is_active"] is True


def test_create_duplicate_account(client):
    """Test that creating duplicate account fails."""
    # Create first account
    client.post(
        "/accounts/",
        json={"email": "duplicate@example.com", "name": "First"},
    )
    
    # Try to create duplicate
    resp = client.post(
        "/accounts/",
        json={"email": "duplicate@example.com", "name": "Second"},
    )
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]


def test_list_accounts(client):
    """Test listing all accounts."""
    # Create a couple of accounts
    client.post("/accounts/", json={"email": "list1@example.com"})
    client.post("/accounts/", json={"email": "list2@example.com"})
    
    # List all accounts
    resp = client.get("/accounts/")
    assert resp.status_code == 200
    data = resp.json()
    assert "accounts" in data
    assert len(data["accounts"]) >= 2


def test_get_account_details(client):
    """Test getting account details."""
    # Create account
    create_resp = client.post(
        "/accounts/",
        json={"email": "details@example.com", "name": "Details Test"},
    )
    account_id = create_resp.json()["account"]["id"]
    
    # Get details
    resp = client.get(f"/accounts/{account_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["account"]["email"] == "details@example.com"
    assert data["account"]["name"] == "Details Test"


def test_update_account(client):
    """Test updating account settings."""
    # Create account
    create_resp = client.post(
        "/accounts/",
        json={"email": "update@example.com"},
    )
    account_id = create_resp.json()["account"]["id"]
    
    # Update account
    resp = client.patch(
        f"/accounts/{account_id}",
        json={
            "name": "Updated Name",
            "fetch_enabled": False,
            "fetch_interval_minutes": 30,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["account"]["name"] == "Updated Name"
    assert data["account"]["fetch_enabled"] is False
    assert data["account"]["fetch_interval_minutes"] == 30


def test_update_account_tokens(client):
    """Test updating account OAuth tokens."""
    # Create account
    create_resp = client.post(
        "/accounts/",
        json={"email": "tokens@example.com"},
    )
    account_id = create_resp.json()["account"]["id"]
    
    # Update tokens
    resp = client.patch(
        f"/accounts/{account_id}/tokens",
        json={
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["account"]["access_token"] == "new_access_token"
    assert data["account"]["refresh_token"] == "new_refresh_token"


def test_delete_account(client):
    """Test deleting an account."""
    # Create account
    create_resp = client.post(
        "/accounts/",
        json={"email": "delete@example.com"},
    )
    account_id = create_resp.json()["account"]["id"]
    
    # Delete account
    resp = client.delete(f"/accounts/{account_id}")
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True
    
    # Verify account is deleted
    get_resp = client.get(f"/accounts/{account_id}")
    assert get_resp.status_code == 404


def test_list_active_accounts_only(client):
    """Test listing only active accounts."""
    # Create active and inactive accounts
    active_resp = client.post("/accounts/", json={"email": "active@example.com"})
    inactive_resp = client.post("/accounts/", json={"email": "inactive@example.com"})
    
    # Disable one account
    inactive_id = inactive_resp.json()["account"]["id"]
    client.patch(f"/accounts/{inactive_id}", json={"is_active": False})
    
    # List active only
    resp = client.get("/accounts/", params={"active_only": True})
    assert resp.status_code == 200
    accounts = resp.json()["accounts"]
    
    # Check all returned accounts are active
    for account in accounts:
        assert account["is_active"] is True
