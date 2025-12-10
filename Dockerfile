# Multi-stage Dockerfile for a Python application

# ================================
# Stage 1: Dependencies
# ================================
FROM python:3.11-slim AS deps
WORKDIR /app

# Copy dependency files
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ================================
# Stage 2: Builder (Optional - if any build steps are needed)
# If no build steps are needed, you can skip this stage and copy directly from 'deps' to 'runner'
# ================================
# FROM python:3.11-slim AS builder
# WORKDIR /app
#
# # Copy source code
# COPY . .
#
# # Any build steps here, e.g., compiling protobufs, etc.
# # RUN python setup.py build

# ================================
# Stage 3: Runner
# ================================
FROM python:3.11-slim AS runner
WORKDIR /app

# Create non-root user for security
RUN addgroup --system appuser && adduser --system --uid 1001 appuser

# Copy necessary files from previous stages
COPY --from=deps /app/ .
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 5000 # TODO: Change port if needed

# Health check (Example - adjust based on your application's health endpoint)
# HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
#   CMD curl --fail http://localhost:5000/health || exit 1 # TODO: Adjust health check URL

# Start the application
CMD ["python", "main.py"] # TODO: Adjust entrypoint if needed