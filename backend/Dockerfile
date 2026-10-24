# Versões: mantenha em sincronia com .python-version e backend-ci.yml
# (POETRY_VERSION). `make check-pins` confere. Não dá para ler esses arquivos
# aqui: o contexto de build é backend/.
ARG PYTHON_VERSION=3.12
ARG POETRY_VERSION=2.4.1

FROM python:${PYTHON_VERSION}-slim

ARG POETRY_VERSION

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
