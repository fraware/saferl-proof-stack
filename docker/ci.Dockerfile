# Proof + RL + Fireworks CLI
FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Install Lean (headless)
RUN curl -s https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | bash -s -- -y
ENV PATH="/root/.elan/bin:$PATH"

# Optionally install Fireworks CLI or other tools

COPY . /workspace 