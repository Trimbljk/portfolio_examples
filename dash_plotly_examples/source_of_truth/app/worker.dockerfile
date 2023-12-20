FROM python:3.11-slim

COPY Pipfile* /

RUN pip install --no-cache-dir "pipenv==2023.2.4" \
    && pipenv install --system

COPY app/ /app/
WORKDIR /

CMD ["celery", "--app=app", "worker", "--beat", "--loglevel=INFO"]
