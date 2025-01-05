# Stage 1: Builder
FROM python:3.12-alpine AS builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip wheel --no-cache-dir -r requirements.txt -w /wheels


# Stage 2: Final Image
FROM python:3.12-alpine
WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

ENV PYTHONUNBUFFERED=1

COPY . /app/
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
