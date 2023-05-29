###############################################
# Haskell Compile Image
###############################################
FROM haskell:slim as haskell-base

COPY ./additional_stuff/ /opt/parser
WORKDIR /opt/parser
RUN ghc parser.hs -o parser
###############################################
# Base Image
###############################################
FROM python:3.10-slim-buster as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.2 \
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
#RUN apk update \
#    && apk add \
#    curl \
#    build-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

FROM builder-base as builder-prod

RUN poetry install --no-dev

FROM builder-base as builder-test

RUN poetry install

FROM python-base as test
COPY --from=builder-test $PYSETUP_PATH $PYSETUP_PATH
COPY --from=haskell-base /opt/parser/parser /test/parser

COPY ./give_money_bot /test/give_money_bot/
COPY ./tests /test/tests/

WORKDIR /test

CMD ["python", "-m", "pytest"]

###############################################
# Production Image
###############################################
FROM python-base as production
COPY --from=builder-prod $PYSETUP_PATH $PYSETUP_PATH
COPY --from=haskell-base /opt/parser/parser /prod/parser

COPY ./give_money_bot /prod/give_money_bot/
COPY ./docker/docker-entrypoint.sh /prod/docker-entrypoint.sh
COPY ./alembic.ini /prod/alembic.ini
RUN chmod +x /prod/docker-entrypoint.sh

WORKDIR /prod

ENTRYPOINT ./docker-entrypoint.sh $0 $@
