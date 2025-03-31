FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false

RUN touch .force_rebuild3

COPY src/ ./src/

RUN poetry install --no-interaction --no-ansi --only main

CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8000"]
