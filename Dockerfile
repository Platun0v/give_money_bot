###############################################
# Base Image
###############################################
FROM python:3.11-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
###############################################
# Builder Image
###############################################
FROM python-base AS builder-base

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

FROM builder-base AS builder-prod

RUN poetry install --no-root --without dev

FROM builder-base AS builder-test

RUN poetry install

FROM python-base AS test
COPY --from=builder-test $PYSETUP_PATH $PYSETUP_PATH

COPY ./give_money_bot /test/give_money_bot/
COPY ./tests /test/tests/

WORKDIR /test

CMD ["python", "-m", "pytest"]

###############################################
# Production Image
###############################################
FROM python-base AS production
COPY --from=builder-prod $PYSETUP_PATH $PYSETUP_PATH

COPY ./give_money_bot /prod/give_money_bot/
COPY ./docker/docker-entrypoint.sh /prod/docker-entrypoint.sh
COPY ./alembic.ini /prod/alembic.ini
RUN chmod +x /prod/docker-entrypoint.sh

WORKDIR /prod

ENTRYPOINT ["./docker-entrypoint.sh"]
