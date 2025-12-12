from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.scheduler import (
    add_account_schedule,
    remove_account_schedule,
    schedule_account_fetches,
    get_scheduler,
)
from services.account_service import get_account


router = APIRouter()


class ScheduleUpdate(BaseModel):
    account_id: int
    interval_minutes: int = Field(..., ge=5, le=1440, description="Fetch interval in minutes (5-1440, minimum 5 to avoid Gmail API rate limits)")


@router.post("/start")
def start_all_schedules():
    """Start scheduled email fetching for all active accounts."""
    schedule_account_fetches()
    scheduler = get_scheduler()
    jobs = scheduler.get_jobs()
    return {
        "message": "Schedules started",
        "active_jobs": len(jobs),
        "jobs": [{"id": job.id, "next_run": job.next_run_time} for job in jobs]
    }


@router.post("/account")
def add_schedule(payload: ScheduleUpdate):
    """Add or update a schedule for a specific account."""
    account = get_account(payload.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    add_account_schedule(
        account_id=payload.account_id,
        account_email=account.email,
        interval_minutes=payload.interval_minutes,
    )
    return {
        "message": f"Schedule added for account {account.email}",
        "interval_minutes": payload.interval_minutes
    }


@router.delete("/account/{account_id}")
def remove_schedule(account_id: int):
    """Remove a schedule for a specific account."""
    remove_account_schedule(account_id)
    return {"message": f"Schedule removed for account {account_id}"}


@router.get("/jobs")
def list_scheduled_jobs():
    """List all scheduled jobs."""
    scheduler = get_scheduler()
    jobs = scheduler.get_jobs()
    return {
        "jobs": [
            {
                "id": job.id,
                "next_run": job.next_run_time,
                "trigger": str(job.trigger),
            }
            for job in jobs
        ]
    }
