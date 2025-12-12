import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Use a throwaway sqlite DB for tests
os.environ["DATABASE_URL"] = "sqlite:///./test_emails.db"

from app import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    # ensure test DB is clean per module
    db_path = Path("test_emails.db")
    if db_path.exists():
        db_path.unlink()
    with TestClient(app) as c:
        yield c
    if db_path.exists():
        db_path.unlink()


def test_fetch_sample_and_list(client):
    resp = client.get("/gmail/fetch", params={"use_sample": True})
    assert resp.status_code == 200
    data = resp.json()
    assert "emails" in data
    assert len(data["emails"]) > 0

    list_resp = client.get("/gmail/list")
    assert list_resp.status_code == 200
    listed = list_resp.json()["emails"]
    assert len(listed) == len(data["emails"])


def test_metrics_increment(client):
    client.get("/gmail/fetch", params={"use_sample": True})
    metrics_resp = client.get("/metrics")
    assert metrics_resp.status_code == 200
    body = metrics_resp.text
    assert "email_fetch_total" in body


def test_categorize_persists(client):
    resp = client.post(
        "/categorize/email",
        json={"subject": "Invoice due", "body": "Your payment is pending", "gmail_id": "g-1"},
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["category"]
    assert payload["email"]["gmail_id"] == "g-1"


def test_health_endpoints(client):
    assert client.get("/").status_code == 200
    assert client.get("/healthz").status_code == 200
    assert client.get("/readiness").status_code == 200


def test_assistant_reply_mock(monkeypatch, client):
    from services import gpt_service

    def _fake_reply(prompt: str) -> str:
        return f"echo:{prompt}"

    monkeypatch.setattr(gpt_service, "generate_reply", _fake_reply)
    resp = client.post("/assistant/reply", json={"prompt": "hello"})
    assert resp.status_code == 200
    assert resp.json()["reply"] == "echo:hello"
