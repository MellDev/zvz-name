# Backend

API FastAPI para o sistema ZvZ.

## Como rodar localmente

1. Crie `.env` a partir de `.env.example`.
2. Instale dependências:

```bash
cd backend
python -m pip install -r requirements.txt
```

3. Execute:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. A API estará disponível em `http://localhost:8000`.

## Migrations

```bash
cd backend
alembic upgrade head
```

## Testes

```bash
cd backend
pytest
```
