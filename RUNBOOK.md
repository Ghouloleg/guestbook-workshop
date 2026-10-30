# Runbook

## Start or inspect the local stack

Create `.env` from `.env.example` and set a strong `POSTGRES_PASSWORD`. Never commit `.env` or paste its contents into logs or issue reports.

```powershell
docker compose up --build -d --wait
docker compose ps
Invoke-RestMethod http://localhost:8000/health
```

Expected health response: `{"status":"ok"}`. The app is available at `http://localhost:8000`; interactive API docs are at `/docs`.

## Roll out a release

Use the immutable version tag from GHCR, not `latest`. Authenticate to GHCR first if the package is private. In PowerShell, set the image and version in the current terminal session:

```powershell
$env:GUESTBOOK_IMAGE = "ghcr.io/OWNER/REPOSITORY"
$env:GUESTBOOK_TAG = "1.2.0"
docker compose pull app
docker compose up -d --no-build app
docker compose ps
Invoke-RestMethod http://localhost:8000/health
```

Replace `OWNER/REPOSITORY` and the version with values from the GitHub Packages page. Check the service logs if the health check does not become healthy:

```powershell
docker compose logs --tail 100 app
docker compose logs --tail 100 db
```

## Roll back

Record the currently deployed image tag before each rollout. To revert, use the same commands above with the previous known-good tag, then verify `/health` and `/messages`:

```powershell
$env:GUESTBOOK_TAG = "1.1.0"
docker compose pull app
docker compose up -d --no-build app
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/messages
```

Do not run `docker compose down -v` during a rollback. The database is a separate service with a named volume, so changing only the app image preserves guestbook entries.

## Troubleshooting

- App is unhealthy: inspect `docker compose logs --tail 100 app`; confirm the container starts and `/health` responds.
- App cannot connect to PostgreSQL: inspect database logs and `docker compose ps`; Compose waits for the database health check before starting the app. Confirm `.env` values are consistent and restart with `docker compose up -d` after correcting them.
- Port 8000 is occupied: change the host side of the `ports` mapping in `compose.yaml` and recreate the app container.
- Data is missing: confirm the `postgres_data` volume is present with `docker volume ls`. Avoid deleting volumes; restore from your external backup process if the volume was lost.
- A new release fails: pin `GUESTBOOK_TAG` to the previous version and follow the rollback steps. Preserve logs and the failing tag for diagnosis.

## Database compatibility

There are no versioned schema migrations yet. Startup only creates the existing `messages` table when absent, and a rollback changes only the application image; it does not revert or delete database data. For future schema changes, use expand-and-contract: first add nullable columns/tables or compatible indexes, deploy code that supports both shapes, backfill, and only remove old fields in a later release after no deployed version needs them. Never make a release depend on a destructive migration that the previous image cannot tolerate.