# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Final
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY . .

# Create static directory to avoid errors
RUN mkdir -p static

# Collect static files (Mock secrets to allow build to succeed without .env)
RUN DJANGO_SECRET_KEY=collectstatic-only \
    DATABASE_URL=sqlite:///:memory: \
    STRIPE_SECRET_KEY=none \
    STRIPE_PUBLIC_KEY=none \
    STRIPE_WEBHOOK_SECRET=none \
    python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--config", "gunicorn.conf.py", "config.wsgi:application"]
