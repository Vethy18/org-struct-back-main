FROM python:3.13-bullseye AS build-stage

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.13-bullseye AS release-stage

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=build-stage ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY org_struct_back ./org_struct_back

ENTRYPOINT ["uvicorn", "org_struct_back.app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]