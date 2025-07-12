FROM python:3.13-slim

ENV FUNCTION_TARGET=function_handler \
    FUNCTION_SIGNATURE_TYPE=http \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir functions-framework

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["functions-framework", "--target=function_handler"]
