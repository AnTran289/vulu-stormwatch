# VULU StormWatch

A Python weather data pipeline and read-only API for Vietnam, built as the
weather and rainfall-risk service for VULU.

StormWatch turns upstream forecasts into stored hourly and daily weather data,
rainfall-based risk indicators, and map-ready API responses. The repository
demonstrates backend development, ETL design, database migrations, automated
testing, and container deployment.

**Stack:** Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL, Alembic, pandas,
Docker, GitHub Actions, and AWS ECS/ECR/S3 deployment integrations.

## Engineering highlights

- Separate extraction, transformation, and persistence stages with typed models.
- Per-location retries with exponential backoff and persisted failure history.
- PostgreSQL advisory locking to prevent concurrent pipeline runs.
- Hourly and daily forecasts exposed through a typed, read-only API.
- Rainfall scoring using daily totals, peak three-hour intensity, and preceding
  48-hour rainfall, with threshold tests.
- Database migrations, schema isolation, and CI checks for linting, types,
  tests, migrations, and Docker builds.

The checked-in province coordinate CSV supports running the pipeline without
the main VULU backend. The `sync_locations.py` script is an optional integration
with that backend.

For preparing a separate public portfolio copy, see
[the publication guide](PUBLIC_RELEASE.md).

StormWatch is VULU's isolated weather and flood-risk reference service. It owns
weather extraction, transformation, persistence, risk calculation, and its
read-only FastAPI surface.

> **Important:** StormWatch risk levels are reference indicators derived from
> forecast rainfall. They are not official flood warnings and must not replace
> guidance from Vietnamese authorities or emergency services.

## Architecture and service boundary

```text
Open-Meteo
    |
    v
StormWatch ETL: extract -> transform -> risk calculation -> load
    |
    v
PostgreSQL (weather, daily forecasts, risk, run/failure history)
    |
    v
StormWatch FastAPI :8001
    |
    v
VULU frontend
```

The main VULU backend on port `8000` does not own StormWatch weather or risk
routes, models, or ETL execution. StormWatch API runs on port `8001`.

## API

- `GET /health`
- `GET /status` (latest run, latest successful update, failure count, freshness)
- `GET /risk/map?forecast_date=YYYY-MM-DD`
- `GET /weather/map?forecast_date=YYYY-MM-DD`
- `GET /weather/{area_code}/forecast`
- `GET /weather/{area_code}/hourly?forecast_date=YYYY-MM-DD`
- Interactive documentation: `http://127.0.0.1:8001/docs`

Successful forecast endpoints return typed JSON lists. A request with no
matching data returns `404`; a database availability failure returns `503`;
invalid or missing query parameters use FastAPI's `422` validation response.

## Configuration

Application code always reads `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`,
`DB_PASSWORD`, and `DB_SCHEMA`. Switching environments does not require code
changes. Use `DB_SCHEMA=stormwatch` when sharing a PostgreSQL database with the
main VULU backend. Runtime connections then use `stormwatch,public` as their
search path, while Alembic records StormWatch revisions in
`stormwatch.alembic_version` and leaves `public.alembic_version` untouched.

- Host-based local development: copy `.env.example` to `.env`.
- Docker with local Supabase: copy `.env.docker.local.example` to
  `.env.docker.local`.
- Supabase Cloud later: copy `.env.supabase.example` to `.env.supabase` and use
  the exact Session pooler values from the Supabase dashboard.
- Production: inject values matching `.env.production.example` from the
  deployment platform's secret/configuration store.

Do not commit real passwords or generated environment files.

## Local development

Start a local PostgreSQL database, copy `.env.example` to `.env`, update the database settings, then install StormWatch:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

Apply migrations to the selected local database and run the API/ETL:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn stormwatch.api.main:app --reload --port 8001
.\.venv\Scripts\python.exe scripts\run_pipeline.py
```

StormWatch owns both the current `/api/weather/*` contract and the legacy
`/weather/*`, `/risk/*`, and `/status` read routes. For example:

```powershell
curl.exe http://localhost:8001/api/weather/provinces
curl.exe http://localhost:8001/api/weather/status
```

Each run retries failed provinces with exponential backoff. `pipeline_runs`
stores totals and final status; `pipeline_failures` stores province code/name,
failed stage, error, attempt, and timestamp—including transient failures that
later recover.

## Docker

Run migrations and the isolated API against local Supabase:

```powershell
docker compose up migrate api --build
```

The API and scheduled job use the `stormwatch-vulu:local` image. Targeted bind
mounts provide live source updates without mounting the Windows virtual
environment into Linux. The API stays online independently of ETL execution.
The built-in `run_worker.py` scheduler remains disabled and retained for review.

The portfolio copy includes CI. Production scheduling requires separate configuration.The pipeline also acquires a PostgreSQL session advisory lock before doing any
work. This protects against overlap across GitHub Actions, manual runs, and
other schedulers. A competing invocation logs that it was skipped and exits
successfully; PostgreSQL releases the lock automatically if the session ends.

Run ETL once, independently, using the same image and configuration:

```powershell
docker compose --profile scheduled-job run --rm worker
```

Compose defaults to `.env.docker.local.example`. To use another file, set
`STORMWATCH_ENV_FILE` before starting services:

```powershell
$env:STORMWATCH_ENV_FILE = ".env.docker.local"
docker compose up migrate api --build
```

The image and application code stay unchanged when the environment changes.

## Production deployment

Build and publish the image, create `.env.production` from secure deployment
settings, then start the production profile:

```powershell
docker build -t registry.example/stormwatch-vulu:VERSION .
$env:STORMWATCH_IMAGE = "registry.example/stormwatch-vulu:VERSION"
docker compose -f compose.production.yml up -d
```

The production profile runs `stormwatch-api`, a controlled migration step, and
an Nginx reverse proxy. The one-shot `stormwatch-job` is separate and uses the
same immutable image. A platform scheduler should invoke it hourly:

```powershell
docker compose -f compose.production.yml --profile scheduled-job run --rm --no-deps stormwatch-job
```

The production compose profile is provided as a deployment example. Configure your own database, registry, and scheduler before using it.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The suite covers HTTP retries, extract/storage behavior, risk thresholds,
risk-input construction, and a small SQLite-backed repository/API flow.

GitHub Actions runs Ruff, mypy, the complete pytest suite, and a Docker image
build for pushes and pull requests.

## Database migrations

StormWatch owns `locations`, `weather_forecasts`, `daily_weather_forecasts`,
`pipeline_runs`, `pipeline_failures`, and `flood_risk_forecasts`. Alembic
autogeneration is restricted to StormWatch-owned tables.

For an existing database that already has the baseline tables, verify its
schema before stamping or upgrading. Never stamp or migrate an unverified
Supabase Cloud database.

