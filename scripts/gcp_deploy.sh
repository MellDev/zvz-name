#!/usr/bin/env bash
set -euo pipefail

export CLOUDSDK_CORE_DISABLE_PROMPTS=1

# Script de deploy para GCP Cloud Run + Cloud SQL + Artifact Registry
# Uso: editar as variáveis abaixo e executar:
#   chmod +x scripts/gcp_deploy.sh
#   ./scripts/gcp_deploy.sh

PROJECT_ID="zvz-name"
PROJECT_NUMBER="970261875556"
REGION="us-central1"
REPO_NAME="zvz-name-repo"
BACKEND_IMAGE="backend"
FRONTEND_IMAGE="frontend"
ARTIFACT_HOST="${REGION}-docker.pkg.dev"
DB_INSTANCE_NAME="zvz-postgres"
DB_ROOT_PASSWORD="postgres" # Troque para senha segura
DB_USER="postgres"
DB_NAME="zvz"

# 1) Configurar projeto
gcloud config set project ${PROJECT_ID}

# 2) Habilitar APIs necessárias
gcloud services enable run.googleapis.com sqladmin.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com iam.googleapis.com cloudbuild.googleapis.com --quiet

# 3) Criar Artifact Registry (se não existir)
if ! gcloud artifacts repositories describe ${REPO_NAME} --location=${REGION} >/dev/null 2>&1; then
  gcloud artifacts repositories create ${REPO_NAME} --repository-format=docker --location=${REGION} --description="Docker repo for zvz-name"
fi

# 4) Build e push das imagens (usando Cloud Build)
gcloud builds submit --quiet --tag ${ARTIFACT_HOST}/${PROJECT_ID}/${REPO_NAME}/${BACKEND_IMAGE}:latest backend
gcloud builds submit --quiet --tag ${ARTIFACT_HOST}/${PROJECT_ID}/${REPO_NAME}/${FRONTEND_IMAGE}:latest frontend

# 5) Criar Cloud SQL (Postgres)
if ! gcloud sql instances describe ${DB_INSTANCE_NAME} --project=${PROJECT_ID} --format=json >/dev/null 2>&1; then
  gcloud sql instances create ${DB_INSTANCE_NAME} \
    --database-version=POSTGRES_16 \
    --cpu=1 --memory=4GiB --region=${REGION} \
    --root-password=${DB_ROOT_PASSWORD}
  # Criar database
  gcloud sql databases create ${DB_NAME} --instance=${DB_INSTANCE_NAME}
fi

# 6) Obter connection name
CONN_NAME="$(gcloud sql instances describe ${DB_INSTANCE_NAME} --format='value(connectionName)')"
echo "Cloud SQL connection name: ${CONN_NAME}"

# 7) Deploy do backend no Cloud Run
# DATABASE_URL usando socket unix do Cloud SQL para Cloud Run
DATABASE_URL="postgresql+psycopg://$DB_USER:$DB_ROOT_PASSWORD@/$DB_NAME?host=/cloudsql/${CONN_NAME}"
gcloud run deploy zvz-backend \
  --image ${ARTIFACT_HOST}/${PROJECT_ID}/${REPO_NAME}/${BACKEND_IMAGE}:latest \
  --platform managed --region ${REGION} \
  --add-cloudsql-instances ${CONN_NAME} \
  --set-env-vars DATABASE_URL="${DATABASE_URL}",SECRET_KEY="REPLACE_ME_SECRET" \
  --allow-unauthenticated --quiet

# 8) Deploy do frontend (pode apontar para o backend público)
gcloud run deploy zvz-frontend \
  --image ${ARTIFACT_HOST}/${PROJECT_ID}/${REPO_NAME}/${FRONTEND_IMAGE}:latest \
  --platform managed --region ${REGION} \
  --set-env-vars NEXT_PUBLIC_API_BASE_URL="https://$(gcloud run services describe zvz-backend --region=${REGION} --platform=managed --format='value(status.url)')" \
  --allow-unauthenticated --quiet


echo "Deploy concluído. Backend e Frontend no Cloud Run. Verifique serviços via:
  gcloud run services list --region=${REGION} --platform=managed"
