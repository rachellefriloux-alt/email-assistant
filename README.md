# Gmail Email Assistant

AI-powered Gmail helper that fetches, categorizes, and summarizes emails with GPT-powered reply suggestions. Ships with backend (FastAPI), frontend (React + Vite + Tailwind), Docker/Helm/Kubernetes/Terraform artifacts, monitoring, CI/CD skeleton, and a sample dataset for offline testing.

## Features

- Gmail fetch (OAuth) with optional bundled sample data for offline use.
- AI categorization (zero-shot transformer + keyword fallback) and GPT reply generation.
- React dashboard with dark/light toggle, category tabs, assistant panel, and GPT suggestion buttons.
- Docker Compose for local dev; Helm charts and raw k8s manifests for clusters.
- Terraform starters for AWS and GCP; GitHub Actions CI/CD example.
- Monitoring stack (Prometheus + Grafana) with alerting via Alertmanager.

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

- `GET /` health check
- `GET /healthz` liveness
- `GET /readiness` readiness
- `GET /gmail/fetch?use_sample=true|false` fetch Gmail or sample data
- `POST /categorize/email` → `{ subject, body }`
- `POST /assistant/reply` → `{ prompt }`

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
