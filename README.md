# Gmail Email Assistant

AI-powered Gmail helper that fetches, categorizes, and summarizes emails with GPT-powered reply suggestions. Ships with backend (FastAPI), frontend (React + Vite + Tailwind), Docker/Helm/Kubernetes/Terraform artifacts, monitoring, CI/CD skeleton, and a sample dataset for offline testing.

## Features

- **Email Management**:
  - Gmail fetch (OAuth) with optional bundled sample data for offline use
  - Advanced search and filtering (by sender, subject, category, date range, read/starred status)
  - Multi-account support with per-account settings
  - Scheduled email fetching with configurable intervals
- **AI-Powered Features**:
  - AI categorization (zero-shot transformer + keyword fallback)
  - GPT-powered reply generation
  - Email sentiment and urgency analysis
- **Reply Templates**:
  - Create and manage reusable reply templates
  - Variable substitution (e.g., {{name}}, {{order_id}})
  - Template usage tracking
- **Infrastructure**:
  - React dashboard with dark/light toggle, category tabs, assistant panel
  - Docker Compose for local dev; Helm charts and raw k8s manifests for clusters
  - Terraform starters for AWS and GCP; GitHub Actions CI/CD example
  - Monitoring stack (Prometheus + Grafana) with alerting via Alertmanager
  - SQLite for development, PostgreSQL for production (see [migration guide](docs/postgresql-migration.md))

## Prerequisites

- Python 3.10+
- Node 18+
- Docker (optional but recommended)
- An OpenAI API key (set `OPENAI_API_KEY`)
- Gmail OAuth credentials (`credentials.json`) if you want live Gmail access

## Quickstart (Local dev)

```bash
python -m venv .venv && source .venv/bin/activate  # or use your preferred venv
cd backend && pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..

# Start services (backend on 8000, frontend on 3000)
./start.sh
```

### Environment variables

Create a `.env` at the repo root (Docker Compose already consumes it) with at least:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_CLIENT_ID=your_google_client_id_here
ALLOWED_ORIGINS=http://localhost:3000
DATABASE_URL=sqlite:///./emails.db
VITE_API_BASE=http://localhost:8000
```

- `ALLOWED_ORIGINS` lets the backend CORS match your frontend URL.
- `DATABASE_URL` can point to Postgres (e.g., `postgresql://user:pass@host:5432/db`).
- `VITE_API_BASE` sets the frontend API base at build/runtime; defaults to `http://localhost:8000`.

### Git User Configuration

To ensure commits and PRs are associated with the correct identity, configure git local `user.name` and `user.email` for this repository.

- **Option 1 (Makefile)**: Set environment variables `GIT_USER_NAME` and `GIT_USER_EMAIL`, then run:

```bash
make git-config
```

- **Option 2 (scripts)**: Run the helper scripts directly:

- Unix/macOS: `./docs/scripts/setup-git.sh`
- Windows PowerShell: `./docs/scripts/setup-git.ps1`

- **Check current config**: `make check-git-config` or `git config --get user.name` and `git config --get user.email`.

These commands set the repo-local config (not global), so your system-level git config remains unchanged.

### Try with sample emails (no Gmail needed)

- Frontend loads sample data by default.
- You can hit the API directly: `GET http://localhost:8000/gmail/fetch?use_sample=true`.

## Docker Compose

```bash
docker-compose up --build
```

- Backend: <http://localhost:8000>
- Frontend: <http://localhost:3000>

## API Endpoints (core)

### Health & Status
- `GET /` - Health check
- `GET /healthz` - Liveness probe
- `GET /readiness` - Readiness probe

### Email Operations
- `GET /gmail/fetch?use_sample=true|false` - Fetch Gmail or sample data
- `GET /gmail/list` - List saved emails with pagination
- `GET /gmail/search` - Search emails with filters (query, sender, category, date range, etc.)
- `POST /gmail/delete` - Delete emails
- `POST /gmail/move` - Move emails to label

### AI & Categorization
- `POST /categorize/email` - Categorize email: `{ subject, body }`
- `POST /assistant/reply` - Generate reply: `{ prompt }`
- `POST /assistant/gemini/summarize` - Summarize email with Gemini
- `POST /assistant/gemini/actions` - Extract action items
- `POST /assistant/gemini/rewrite` - Rewrite draft: `{ text, tone }`

### Account Management
- `POST /accounts/` - Create new account
- `GET /accounts/` - List all accounts
- `GET /accounts/{id}` - Get account details
- `PATCH /accounts/{id}` - Update account settings
- `PATCH /accounts/{id}/tokens` - Update OAuth tokens
- `DELETE /accounts/{id}` - Delete account

### Template Management
- `POST /templates/` - Create new template
- `GET /templates/` - List templates
- `GET /templates/{id}` - Get template details
- `GET /templates/{id}/variables` - Get template variables
- `PATCH /templates/{id}` - Update template
- `DELETE /templates/{id}` - Delete template
- `POST /templates/render` - Render template with variables

### Scheduler
- `POST /scheduler/start` - Start scheduled fetching for all accounts
- `POST /scheduler/account` - Add/update schedule for account
- `DELETE /scheduler/account/{id}` - Remove schedule
- `GET /scheduler/jobs` - List scheduled jobs

For full API documentation, visit `/docs` when the backend is running.

## Monitoring & Alerting

```bash
cd monitoring
docker-compose up -d
```

- Prometheus: <http://localhost:9090> (rules loaded from `alert.rules.yml`)
- Grafana: <http://localhost:3001> (admin/admin by default)
- Alertmanager: <http://localhost:9093> (configure email/Slack in `alertmanager.yml`)

### Prometheus & Grafana Cheat Sheet

- Reload Prometheus: `curl -X POST http://localhost:9090/-/reload`
- Targets page: <http://localhost:9090/targets>
- Add Prometheus as Grafana data source: `http://prometheus:9090`
- Import dashboards: `monitoring/grafana/dashboards/` (add your JSON files there)

## Helm (Kubernetes)

```bash
helm install email-assistant ./helm \
  --set image.backend=<your-backend-image> \
  --set image.frontend=<your-frontend-image> \
  --set env.OPENAI_API_KEY=<your-key>

# Update values in helm/values.yaml for ingress, replicas, etc.
helm upgrade email-assistant ./helm
helm rollback email-assistant 1
```

## Raw Kubernetes Manifests

- `k8s/backend-deployment.yaml`, `k8s/frontend-deployment.yaml`, `k8s/service.yaml`, `k8s/ingress.yaml`
- Replace placeholder images and secret references before applying.

## Terraform Starters

- AWS: `terraform/aws/main.tf`
- GCP: `terraform/gcp/main.tf`

```bash
cd terraform/aws   # or terraform/gcp
terraform init
terraform apply    # add -var overrides as needed
terraform destroy  # clean up
```

## CI/CD (GitHub Actions)

- Workflow skeleton at `.github/workflows/deploy.yml` (builds Docker images; extend to push/deploy).
- Add `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets for registry pushes.

## Frontend

- Vite + React + Tailwind.
- Configurable API base via `VITE_API_BASE` (defaults to `http://localhost:8000`).
- Dark/light toggle in header; GPT suggestion buttons in Assistant panel.

## Backend

- FastAPI with CORS enabled for dev.
- GPT model: `gpt-4o-mini` (override in `services/gpt_service.py` if desired).
- Categorization: zero-shot classifier with keyword fallback.

## Sample Data

- `backend/sample_emails.json` for offline testing.

## Video & Mockup

- A realistic light-mode mockup and video walkthrough are not embedded here; recreate using the described UI (header + toggle, category tabs, email list, assistant with GPT buttons) if you need visuals.

## Licensing

MIT (adjust as needed).
