# Public portfolio publication

Suggested repository name: `vulu-stormwatch`.

Suggested GitHub description:

> Weather ETL and rainfall-risk API for Vietnam using Python, FastAPI,
> PostgreSQL, Docker, and AWS deployment integrations.

Suggested topics: `python`, `fastapi`, `postgresql`, `etl`, `weather`, `docker`,
`sqlalchemy`, `github-actions`.

## Prepare the public copy

The working repository is connected to `Flood-Aid/vulu-weather-pipeline` and
contains production deployment workflows. For a personal portfolio copy,
export reviewed source into a separate directory and start a fresh Git history.
Keep the production checkout and its remote intact.

Include application source, tests, scripts, migrations, Docker files, example
environment files, CI, and `data/reference/province_coordinates.csv`.
Exclude real environment files, credentials, Python bytecode, virtual
environments, generated package metadata, raw forecast downloads, and logs.
Some generated files are already tracked in the current repository; `.gitignore`
alone does not remove them from a public export or previous commits.

Review the existing untracked `docs/` contents separately before including them.
Keep only the CI workflow in a portfolio copy initially. Production deploy and
pipeline workflows depend on the original AWS infrastructure and GitHub secrets;
they should be deliberately configured for any new repository before enabling.
Replace original AWS account identifiers and deployment targets with documented
configuration placeholders in any deployment examples included in that copy.

Run a secret scan over the exact files to publish. If publishing the existing
repository instead, scan its full Git history as well. A basic pattern check is
not a complete secret audit. Choose a license only after confirming the rights
to publish and license the project and its data.

## Verify and publish

Install development dependencies with `python -m pip install -e ".[dev]"`.
Run `ruff check src scripts tests`, `mypy`, and `pytest -q` in the prepared copy.
The CI workflow also checks PostgreSQL migrations and Docker builds.

Authenticate GitHub CLI with `gh auth login -h github.com`, then create the
public repository from the prepared copy with the selected account and name.
Set its description and topics, and pin it on the personal GitHub profile.

## Standalone local database

The API and pipeline require PostgreSQL; they do not require Supabase-specific
features. Create a local database, copy `.env.example` to `.env`, and set
`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `DB_SCHEMA`
to match that database. Then follow the migration and run commands in the README.
The supplied Docker development profile expects an external database and does
not start PostgreSQL itself.
