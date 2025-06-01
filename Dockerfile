FROM python:3.12-slim AS builder
LABEL org.opencontainers.image.authors="Hubert Kwiatkowski"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12

COPY ./app /app/

EXPOSE 4444

HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:4444 || exit 1

ENTRYPOINT ["python", "main.py"]
