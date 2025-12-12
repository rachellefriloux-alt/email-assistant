# Secret Management (Production)

Keep sensitive values out of images and repos. In production, pull them from a managed secrets store instead of baking them into images or manifests.

## Core secrets

- `OPENAI_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `DATABASE_URL` (if it contains credentials)

## Kubernetes Secrets

- Create secrets:

  ```bash
  kubectl create secret generic openai-secret --from-literal=api-key=$OPENAI_API_KEY
  kubectl create secret generic google-oauth \
    --from-literal=client-id=$GOOGLE_CLIENT_ID \
    --from-literal=client-secret=$GOOGLE_CLIENT_SECRET
  ```

- Deploy: manifests/Helm reference `openai-secret` and `google-oauth` for backend env. Optionally manage them via External Secrets Operator or Secret Store CSI to sync from cloud stores.

## AWS Secrets Manager

- Store secrets:

  ```bash
  aws secretsmanager create-secret --name email-assistant/openai --secret-string "$OPENAI_API_KEY"
  aws secretsmanager create-secret --name email-assistant/google-client-id --secret-string "$GOOGLE_CLIENT_ID"
  aws secretsmanager create-secret --name email-assistant/google-client-secret --secret-string "$GOOGLE_CLIENT_SECRET"
  ```

- Access patterns:
  - EKS: use External Secrets Operator or Secrets Store CSI driver to project into Kubernetes Secrets for the cluster.
  - ECS/Fargate: attach a task role and map Secrets Manager entries into container environment variables.

## GCP Secret Manager

- Store secrets:

  ```bash
  gcloud secrets create email-assistant-openai --data-file <(printf '%s' "$OPENAI_API_KEY")
  gcloud secrets create email-assistant-google-client-id --data-file <(printf '%s' "$GOOGLE_CLIENT_ID")
  gcloud secrets create email-assistant-google-client-secret --data-file <(printf '%s' "$GOOGLE_CLIENT_SECRET")
  ```

- Access patterns:
  - GKE: use Secret Manager CSI Driver or External Secrets Operator; bind Workload Identity so pods can fetch secrets.
  - Cloud Run: map secrets to environment variables with `--set-secrets` during deploy.

## Local development

- `.env` is for local/dev only. Do not commit real secrets.
- For Compose, `env_file: .env` is fine in dev; in prod, inject env vars from your orchestrator or secrets store.
