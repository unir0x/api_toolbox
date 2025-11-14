#!/bin/sh
set -eu

# This script runs as root.

CONFIG_DIR="/app/config"
LOG_DIR="/app/logs"

# --- Prepare Directories & Permissions ---
echo "Ensuring config and log directories exist..."
mkdir -p "${CONFIG_DIR}" "${LOG_DIR}"

echo "Updating permissions for config and logs..."
chown -R appuser:appuser "${CONFIG_DIR}" "${LOG_DIR}"

# --- Start Application ---
echo "Starting Waitress as appuser..."
exec gosu appuser /usr/local/bin/waitress-serve --host 0.0.0.0 --port 8000 main:app
