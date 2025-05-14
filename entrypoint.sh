#!/bin/bash
# Start Supervisor
# Start Supervisor if not already running
if ! ps aux | grep -q "[s]upervisor"; then
    echo "Starting supervisor service ⏳"
    exec /usr/bin/supervisord -nc /etc/supervisor/supervisord.conf
    echo "Supervisor started ✅"
else
    echo "Supervisor is currently running ✅"
fi

exec "$@"
