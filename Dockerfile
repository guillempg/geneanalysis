# -----------------------------
# Stage 1: Builder
# -----------------------------

FROM python:3.12-slim AS builder
WORKDIR /app

# Install build dependencies only for building Python packages

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copy only requirements for caching

COPY requirements.txt .

# Build wheels for all dependencies

RUN pip wheel --wheel-dir=/wheels --no-cache-dir -r requirements.txt

# -----------------------------
# Stage 2: Runtime
# -----------------------------

FROM python:3.12-slim
WORKDIR /app

# Create /data for mounting external files

RUN mkdir -p /data

# Copy wheels from builder and install

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copy only the application code

COPY . .

# Expose Streamlit port

EXPOSE 8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run Streamlit

CMD ["streamlit", "run", "scripts/app_integrada.py"]

