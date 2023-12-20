FROM python:3.11-slim

COPY Pipfile* /
RUN pip install --no-cache-dir "pipenv==2022.7.4" \
    && pipenv install --system

COPY app/ /app/
WORKDIR /app

CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "1800", \
     "--log-level", "debug", \
     "main:server"]
