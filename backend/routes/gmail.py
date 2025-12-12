
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from prometheus_client import Counter
from pydantic import BaseModel

from services.email_store import (
    bulk_archive_emails,
    bulk_delete_emails,
    bulk_mark_read,
    bulk_star_emails,
    delete_by_gmail_ids,
    list_emails,
    search_emails,
    upsert_emails,
)
from services.gmail_service import (
    authenticate_gmail,
    delete_emails,
    fetch_emails,
    load_sample_emails,
    move_emails_to_label,
)


router = APIRouter()

EMAIL_FETCH_COUNTER = Counter(
    "email_fetch_total", "Count of emails fetched and stored", ["source"]
)
EMAIL_DELETE_COUNTER = Counter(
    "email_delete_total", "Count of emails deleted locally", ["remote"]
)
EMAIL_MOVE_COUNTER = Counter(
    "email_move_total", "Count of emails moved to labels locally", ["remote"]
)


class DeleteRequest(BaseModel):
    gmail_ids: List[str]
    skip_remote: bool = False


class MoveRequest(BaseModel):
    gmail_ids: List[str]
    label_id: str
    skip_remote: bool = False


class BulkOperationRequest(BaseModel):
    email_ids: List[int]


@router.get("/fetch")
def fetch_gmail_emails(use_sample: bool = Query(False, description="Use bundled sample data instead of Gmail")):
    emails = load_sample_emails() if use_sample else fetch_emails(authenticate_gmail())
    records = upsert_emails(emails)
    EMAIL_FETCH_COUNTER.labels(source="sample" if use_sample else "live").inc(len(records))
    return {"emails": [rec.model_dump() for rec in records]}


@router.get("/list")
def list_saved_emails(
    status: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    records = list_emails(status=status, category=category, limit=limit, offset=offset)
    return {"emails": [rec.model_dump() for rec in records]}


@router.post("/delete")
def delete_saved_emails(payload: DeleteRequest):
    deleted_count = delete_by_gmail_ids(payload.gmail_ids)
    if not payload.skip_remote:
        try:
            delete_emails(authenticate_gmail(), payload.gmail_ids)
        except Exception as exc:  # pragma: no cover - best-effort remote
            raise HTTPException(status_code=502, detail=f"Failed to delete in Gmail: {exc}")
    EMAIL_DELETE_COUNTER.labels(remote=str(not payload.skip_remote)).inc(deleted_count)
    return {"deleted": deleted_count}


@router.post("/move")
def move_emails(payload: MoveRequest):
    if not payload.label_id:
        raise HTTPException(status_code=400, detail="label_id is required")
    if not payload.skip_remote:
        try:
            move_emails_to_label(authenticate_gmail(), payload.gmail_ids, payload.label_id)
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=502, detail=f"Failed to move in Gmail: {exc}")
    EMAIL_MOVE_COUNTER.labels(remote=str(not payload.skip_remote)).inc(len(payload.gmail_ids))
    return {"moved": len(payload.gmail_ids)}


@router.get("/search")
def search_saved_emails(
    query: Optional[str] = Query(None, description="Search text in subject, body, or snippet"),
    from_email: Optional[str] = Query(None, description="Filter by sender email"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    is_starred: Optional[bool] = Query(None, description="Filter by starred status"),
    date_from: Optional[datetime] = Query(None, description="Filter emails from this date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="Filter emails until this date (ISO format)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Search and filter emails with multiple criteria."""
    records = search_emails(
        query=query,
        from_email=from_email,
        subject=subject,
        category=category,
        status=status,
        is_read=is_read,
        is_starred=is_starred,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return {"emails": [rec.model_dump() for rec in records], "count": len(records)}


@router.post("/bulk/archive")
def bulk_archive(payload: BulkOperationRequest):
    """Archive multiple emails at once."""
    count = bulk_archive_emails(payload.email_ids)
    return {"archived": count}


@router.post("/bulk/delete")
def bulk_delete(payload: BulkOperationRequest):
    """Delete multiple emails at once."""
    count = bulk_delete_emails(payload.email_ids)
    return {"deleted": count}


@router.post("/bulk/mark-read")
def bulk_mark_as_read(payload: BulkOperationRequest):
    """Mark multiple emails as read."""
    count = bulk_mark_read(payload.email_ids, is_read=True)
    return {"marked_read": count}


@router.post("/bulk/mark-unread")
def bulk_mark_as_unread(payload: BulkOperationRequest):
    """Mark multiple emails as unread."""
    count = bulk_mark_read(payload.email_ids, is_read=False)
    return {"marked_unread": count}


@router.post("/bulk/star")
def bulk_star(payload: BulkOperationRequest):
    """Star multiple emails."""
    count = bulk_star_emails(payload.email_ids, is_starred=True)
    return {"starred": count}


@router.post("/bulk/unstar")
def bulk_unstar(payload: BulkOperationRequest):
    """Unstar multiple emails."""
    count = bulk_star_emails(payload.email_ids, is_starred=False)
    return {"unstarred": count}
