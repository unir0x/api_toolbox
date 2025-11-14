# --- Builder Stage ---
# This stage installs the Python dependencies using a newer, more secure base image.
FROM python:3.11-slim-bookworm AS builder

# Upgrade pip/setuptools to mitigate known vulnerabilities
RUN pip install --no-cache-dir --upgrade pip setuptools

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Final Stage ---
# This stage creates the final, small production image.
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install latest gosu for privilege dropping to mitigate Go CVEs
ARG GOSU_VERSION=1.19
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    dpkgArch="$(dpkg --print-architecture)" && \
    curl -o /usr/local/bin/gosu -sSL "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch" && \
    chmod +x /usr/local/bin/gosu && \
    apt-get purge -y --auto-remove curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy installed packages and binaries from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
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
