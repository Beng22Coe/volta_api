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

## Run in production

```bash
poetry run gunicorn -k uvicorn.workers.UvicornWorker volta_api.main:app --app-dir src
gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 127.0.0.1:8000 --chdir src "volta_api.main:app"
```
