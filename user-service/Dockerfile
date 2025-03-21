FROM python:3.11-slim AS base

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS test
COPY test/requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt
COPY src/ ./src/
COPY test/ ./test/
ENV DATABASE_URL="sqlite:///:memory:"
ENV JWT_SECRET="test-secret-key"
ENV ACCESS_TOKEN_EXPIRE_MINUTES="30"
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS production
COPY src/ .
EXPOSE 8000
CMD ["python", "main.py"]