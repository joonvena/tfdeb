FROM python:3.10.3-alpine

WORKDIR /app

COPY requirements.txt /app

RUN set eux; \
    apk add --no-cache \
        alpine-sdk \ 
        libffi-dev \
    ; \
    addgroup -S tfdeb && adduser -S -H tfdeb -G tfdeb; \
    pip install --no-cache-dir -r requirements.txt; \
    apk del alpine-sdk

COPY --chown=tfdeb:tfdeb . .

USER tfdeb
