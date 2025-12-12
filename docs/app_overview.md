# Email Assistant Overview

Email Assistant is a full-stack Gmail helper. It fetches, categorizes, and summarizes emails, then suggests AI-powered replies. It ships with a FastAPI backend, a React + Vite + Tailwind frontend, and deployable artifacts for Docker, Helm, Kubernetes, and Terraform. A sample dataset makes it usable even without live Gmail access.

### Why it’s notable
- Rich email operations: threading, advanced search, and bulk actions (archive, delete, mark read/unread, star)
- AI categorization and analysis: automatic category creation plus sentiment/urgency insights
- AI writing assistance: GPT-based reply generation alongside Gemini summarization/rewrite
- Productivity tooling: reusable reply templates with variables, multi-account support, and a scheduler for periodic fetches
- Production-minded: monitoring stack (Prometheus/Grafana), CI/CD starter, and Postgres-ready configuration

Overall, the app is a well-structured starter for an AI-assisted email workflow with both local dev convenience and clear paths to production.
