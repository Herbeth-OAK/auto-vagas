#!/bin/bash
# Function to handle signals
handle_signal() {
  echo "Caught signal, stopping services..."
  supervisorctl stop all
  exit 0
}

# Trap signals
trap 'handle_signal' SIGTERM SIGINT

# Start Supervisor
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &

# Wait for Supervisor to start
while true; do
  sleep 1
done