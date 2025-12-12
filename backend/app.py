
import json
import logging
import os
import time
from collections import defaultdict, deque
from typing import Deque

from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from db import init_db
from routes import assistant, categorize, gmail, accounts, scheduler, templates, categories, threads

load_dotenv()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload = {
            "level": record.levelname,
            "time": self.formatTime(record, self.datefmt),
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers = [handler]

app = FastAPI(title="Gmail Email Assistant", version="1.0.0")

# Allow local dev frontends by default; tighten in production via env/config.
allow_origins_env = os.getenv("ALLOWED_ORIGINS")
allow_origins = allow_origins_env.split(",") if allow_origins_env else ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

# Simple in-memory rate limiter per client IP.
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
WINDOW_SECONDS = 60
request_log: dict[str, Deque[float]] = defaultdict(deque)
api_key = os.getenv("API_KEY")
API_KEY_SKIP_PATHS = {"/", "/healthz", "/readiness", "/docs", "/openapi.json", "/metrics"}


@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    if api_key and request.url.path not in API_KEY_SKIP_PATHS:
        provided = request.headers.get("x-api-key")
        if provided != api_key:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = request_log[client_ip]
    while window and now - window[0] > WINDOW_SECONDS:
        window.popleft()
    if not window:
        # drop empty queues to avoid unbounded growth for one-time IPs
        request_log.pop(client_ip, None)
        window = request_log[client_ip]
    if len(window) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    window.append(now)
    try:
        response = await call_next(request)
    except Exception:  # centralized error logging
        logging.exception("Unhandled error")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    return response

app.include_router(gmail.router, prefix="/gmail", tags=["Gmail"])
app.include_router(categorize.router, prefix="/categorize", tags=["Categorization"])
app.include_router(assistant.router, prefix="/assistant", tags=["AI Assistant"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(scheduler.router, prefix="/scheduler", tags=["Scheduler"])
app.include_router(templates.router, prefix="/templates", tags=["Templates"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(threads.router, prefix="/threads", tags=["Threads"])


# Initialize Prometheus instrumentation before startup
Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
async def _startup():
    init_db()
    # Initialize default categories
    from services.category_service import initialize_default_categories
    initialize_default_categories()


@app.get("/", tags=["Health"])
def root():
    return {"message": "Email Assistant API is running"}


@app.get("/healthz", tags=["Health"])
def health() -> dict:
    return {"status": "ok"}


@app.get("/readiness", tags=["Health"])
def readiness() -> dict:
    return {"status": "ready"}
