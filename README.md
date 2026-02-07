# Daladala Live

A FastAPI application for managing daladala (public transport) live tracking data.

## Setup

```bash
poetry install
```

## Run database migrations

```bash
poetry run alembic upgrade head
```

## Run the application

```bash
poetry run uvicorn volta_api.main:app --reload --app-dir src
```
