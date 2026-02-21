FROM python:3.13

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock /app/
RUN poetry install --without dev --no-root

COPY src /app/src
CMD ["poetry", "run", "fastapi", "run", "src/entrypoints/main.py"]