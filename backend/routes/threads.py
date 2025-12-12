from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from services.threading_service import (
    archive_thread,
    get_thread_emails,
    list_threads,
    unarchive_thread,
)


router = APIRouter()


@router.get("/")
def list_email_threads(
    account_id: Optional[int] = None,
    unread_only: bool = False,
    archived_only: bool = False,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List email threads with filters."""
    threads = list_threads(
        account_id=account_id,
        unread_only=unread_only,
        archived_only=archived_only,
        limit=limit,
        offset=offset,
    )
    return {"threads": [thread.model_dump() for thread in threads], "count": len(threads)}


@router.get("/{thread_id}/emails")
def get_thread_messages(thread_id: str, limit: int = Query(100, ge=1, le=500)):
    """Get all emails in a thread."""
    emails = get_thread_emails(thread_id, limit=limit)
    if not emails:
        raise HTTPException(status_code=404, detail="Thread not found or empty")
    return {"emails": [email.model_dump() for email in emails], "count": len(emails)}


@router.post("/{thread_id}/archive")
def archive_email_thread(thread_id: str):
    """Archive a thread."""
    success = archive_thread(thread_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"archived": True}


@router.post("/{thread_id}/unarchive")
def unarchive_email_thread(thread_id: str):
    """Unarchive a thread."""
    success = unarchive_thread(thread_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"unarchived": True}
