# --- Builder Stage ---
# This stage installs the Python dependencies.
FROM python:3.9-slim-bullseye AS builder

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Final Stage ---
# This stage creates the final, small production image.
FROM python:3.9-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install gosu for privilege dropping
RUN apt-get update && apt-get install -y --no-install-recommends gosu && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy installed packages and binaries from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set up the application directory
WORKDIR /app
COPY . .

# Explicitly copy and set permissions for the entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create a non-root user and group
RUN groupadd --system --gid 1001 appuser && useradd --system --uid 1001 --gid appuser appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
