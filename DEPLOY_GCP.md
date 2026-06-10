# Deploy para GCP (Cloud Run) — zvz-name

Pré-requisitos:

- `gcloud` instalado e autenticado (`gcloud auth login`)
- `Docker` (opcional se usar `gcloud builds submit`)
- Permissões no projeto GCP (Editor ou Owner)

Variáveis principais:

- PROJECT_ID: zvz-name
- PROJECT_NUMBER: 970261875556
- REGION: us-central1

Passos resumidos (automatizados em `scripts/gcp_deploy.sh`):

1. Configure o projeto:

```bash
gcloud config set project zvz-name
```

2. Habilite APIs:

```bash
gcloud services enable run.googleapis.com sqladmin.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com iam.googleapis.com
```

3. Crie o repositório do Artifact Registry (docker):

```bash
gcloud artifacts repositories create zvz-name-repo --repository-format=docker --location=us-central1 --description="Docker repo for zvz-name"
```

4. Construa e envie as imagens (Cloud Build):

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/zvz-name/zvz-name-repo/backend:latest backend

gcloud builds submit --tag us-central1-docker.pkg.dev/zvz-name/zvz-name-repo/frontend:latest frontend
```

5. Crie a instância do Cloud SQL (Postgres 16):

```bash
gcloud sql instances create zvz-postgres --database-version=POSTGRES_16 --cpu=1 --memory=4GiB --region=us-central1 --root-password="SENHA_SEGURA"

gcloud sql databases create zvz --instance=zvz-postgres
```

6. Deploy no Cloud Run (backend) conectando ao Cloud SQL:

```bash
# Substitua CONN_NAME pelo connectionName da instância: PROJECT:REGION:INSTANCE
CONN_NAME=$(gcloud sql instances describe zvz-postgres --format='value(connectionName)')

DATABASE_URL="postgresql+psycopg://postgres:SENHA_SEGURA@/zvz?host=/cloudsql/${CONN_NAME}"

gcloud run deploy zvz-backend \
  --image us-central1-docker.pkg.dev/zvz-name/zvz-name-repo/backend:latest \
  --platform managed --region us-central1 \
  --add-cloudsql-instances ${CONN_NAME} \
  --set-env-vars DATABASE_URL="${DATABASE_URL}",SECRET_KEY="REPLACE_ME_SECRET" \
  --allow-unauthenticated
```

7. Deploy do frontend (apontando para API pública):

```bash
gcloud run deploy zvz-frontend \
  --image us-central1-docker.pkg.dev/zvz-name/zvz-name-repo/frontend:latest \
  --platform managed --region us-central1 \
  --set-env-vars NEXT_PUBLIC_API_BASE_URL="https://<BACKEND_URL>" \
  --allow-unauthenticated
```

Verificações pós-deploy:

- Listar serviços Cloud Run:

```bash
gcloud run services list --region=us-central1 --platform=managed
```

- Verificar logs:

```bash
gcloud logs read --project=zvz-name --limit=50
```

Notas de segurança e produção:

- Use o Secret Manager para armazenar `SECRET_KEY` e senhas do banco de dados e use `--set-secrets` no `gcloud run deploy`.
- Configure VPC connectors e regras de ingress/egress se necessário.
- Considere usar Identity-Aware Proxy (IAP) e Cloud Armor para proteção adicional.

Se quiser, posso executar localmente o build das imagens aqui e testar o push, mas para efetuar o deploy real você precisa estar autenticado com `gcloud` nesta máquina ou executar os comandos no seu terminal.
