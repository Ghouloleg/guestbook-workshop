# Guestbook

A small FastAPI guestbook backed by PostgreSQL. The repository includes a locked `uv` environment, Docker Compose for local use, CI checks, and GHCR releases.

## Run locally

Requirements: Docker Compose v2 and PowerShell (or equivalent shell).

```powershell
Copy-Item .env.example .env
```

Set a strong, unique `POSTGRES_PASSWORD` in `.env`, then start the service:

```powershell
docker compose up --build -d --wait
```

Open http://localhost:8000/docs. `docker compose down` stops containers but preserves messages in the named volume. `docker compose down -v` also deletes the database and all messages.

For local development with an available PostgreSQL instance:

```powershell
uv sync --locked --all-groups
uv run uvicorn main:app --reload --host 0.0.0.0
uv run ruff check .
uv run pytest
```

## CI and releases

Pull requests and pushes to `main` run Ruff and pytest. A successful push to `main` publishes `ghcr.io/<owner>/<repository>:latest`. Pushing a semantic version tag such as `v1.2.0` runs the same checks and publishes `:v1.2.0` and `:1.2.0`.

Before tagging, update `CHANGELOG.md` and the project version in `pyproject.toml`. Create and push the tag only after the release commit is on `main`:

```powershell
git tag v1.2.0
git push origin v1.2.0
```

To roll out or roll back an image, set `GUESTBOOK_IMAGE` to `ghcr.io/<owner>/<repository>` and `GUESTBOOK_TAG` to the desired immutable version, then run `docker compose pull app` and `docker compose up -d --no-build app`. Keep PostgreSQL's named volume unchanged. See [RUNBOOK.md](RUNBOOK.md) for the complete procedure and incident checks.

## API

- `GET /` returns the configured greeting.
- `GET /health` reports application health.
- `GET /messages` lists messages, newest first.
- `POST /messages` accepts `{"author": "...", "text": "..."}`.
