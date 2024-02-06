FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt update && apt install --yes --no-install-recommends python3-poetry

COPY . .

RUN poetry install

ENTRYPOINT ["poetry", "run", "archiver"]
