#!/bin/sh

# This script runs as root.

# --- Set Permissions ---
echo "Updating permissions for config and logs..."
# Recursively change ownership of the config and logs directories to the 'appuser'
chown -R appuser:appuser /app/config
chown -R appuser:appuser /app/logs

# --- Start Application ---
# Drop privileges and start the application
echo "Starting Waitress as appuser..."
exec gosu appuser /usr/local/bin/waitress-serve --host 0.0.0.0 --port 8000 main:app
