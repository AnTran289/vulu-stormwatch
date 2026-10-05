FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
COPY alembic.ini ./
COPY alembic ./alembic
COPY src ./src
COPY scripts ./scripts
COPY data/reference ./data/reference

RUN mkdir -p /app/data/raw /app/logs

RUN pip install --no-cache-dir .

EXPOSE 8001

CMD ["uvicorn", "stormwatch.api.main:app", "--host", "0.0.0.0", "--port", "8001"]
