# Minimal image for CI smoke tests (proofstack --help / version).
FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY proofstack ./proofstack

RUN pip install --no-cache-dir "poetry>=1.8,<2" \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["proofstack"]
CMD ["--help"]
