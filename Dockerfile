###############################################
# Haskell Compile Image
###############################################
FROM haskell:9.0.1-buster as haskell-base

COPY ./additional_stuff/parser.hs /opt/
WORKDIR /opt
RUN ghc parser.hs -o parser
###############################################
# Base Image
###############################################
FROM python:3.9-alpine as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.11 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
###############################################
# Builder Image
###############################################
FROM python-base as builder-base
RUN apk update \
    && apk add \
    curl \
    build-base

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

RUN poetry install --no-dev

###############################################
# Production Image
###############################################
FROM python-base as production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY --from=haskell-base /opt/parser /prod/parser

COPY ./give_money_bot /prod/give_money_bot/
COPY ./docker/docker-entrypoint.sh /prod/docker-entrypoint.sh
RUN chmod +x /prod/docker-entrypoint.sh

WORKDIR /prod

ENTRYPOINT ./docker-entrypoint.sh $0 $@
