import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from services.account_service import list_accounts
from services.email_store import upsert_emails
from services.gmail_service import authenticate_gmail, fetch_emails

log = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None


def get_scheduler() -> BackgroundScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
        _scheduler.start()
        log.info("Scheduler started")
    return _scheduler


def fetch_emails_for_account(account_id: int, account_email: str):
    """Background task to fetch emails for a specific account."""
    try:
        log.info(f"Fetching emails for account {account_email} (ID: {account_id})")
        # For now, use the default authentication
        # In production, this should use account-specific tokens
        service = authenticate_gmail()
        emails = fetch_emails(service)
        
        # Add account_id to each email
        for email in emails:
            email['account_id'] = account_id
        
        records = upsert_emails(emails)
        log.info(f"Fetched and stored {len(records)} emails for account {account_email}")
    except Exception as e:
        log.error(f"Error fetching emails for account {account_email}: {e}")


def schedule_account_fetches():
    """Schedule email fetching for all active accounts."""
    scheduler = get_scheduler()
    accounts = list_accounts(active_only=True)
    
    for account in accounts:
        if not account.fetch_enabled:
            continue
        
        job_id = f"fetch_account_{account.id}"
        
        # Remove existing job if it exists
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        
        # Schedule new job
        scheduler.add_job(
            fetch_emails_for_account,
            trigger=IntervalTrigger(minutes=account.fetch_interval_minutes),
            args=[account.id, account.email],
            id=job_id,
            replace_existing=True,
        )
        log.info(f"Scheduled email fetch for {account.email} every {account.fetch_interval_minutes} minutes")


def add_account_schedule(account_id: int, account_email: str, interval_minutes: int):
    """Add or update a schedule for a specific account."""
    scheduler = get_scheduler()
    job_id = f"fetch_account_{account_id}"
    
    # Remove existing job if it exists
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    
    # Add new job
    scheduler.add_job(
        fetch_emails_for_account,
        trigger=IntervalTrigger(minutes=interval_minutes),
        args=[account_id, account_email],
        id=job_id,
        replace_existing=True,
    )
    log.info(f"Scheduled email fetch for {account_email} every {interval_minutes} minutes")


def remove_account_schedule(account_id: int):
    """Remove a schedule for a specific account."""
    scheduler = get_scheduler()
    job_id = f"fetch_account_{account_id}"
    
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        log.info(f"Removed email fetch schedule for account {account_id}")


def shutdown_scheduler():
    """Shutdown the scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown()
        _scheduler = None
        log.info("Scheduler shutdown")
