#!/bin/bash

# This script runs all the necessary components for the Thoughts application.
# It starts Memcached (if not running), the FastAPI server, and the background worker.

# Function to clean up background jobs on exit
cleanup() {
    echo -e "\nShutting down background processes..."
    # Kill the FastAPI server that was started by this script
    if [ -n "$UVICORN_PID" ]; then
        kill $UVICORN_PID
    fi
    exit
}

# Trap SIGINT (Ctrl+C) and EXIT to call the cleanup function
trap cleanup SIGINT EXIT

# 1. Start Memcached
if ! pgrep -x "memcached" > /dev/null
then
    echo "Starting Memcached in the background..."
    memcached -d
    if [ $? -ne 0 ]; then
        echo "Failed to start Memcached. Please ensure it is installed and try starting it manually."
        exit 1
    fi
    sleep 1
else
    echo "Memcached is already running."
fi

# 2. Start the FastAPI server in the background
echo "Starting FastAPI server in the background..."
poetry run uvicorn thoughts.api.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!
echo "FastAPI server started with PID $UVICORN_PID."
sleep 3 # Give server time to start up before the worker starts logging

# 3. Start the worker in the foreground
echo "Starting the background worker..."
echo "Press Ctrl+C to shut down the application (server and worker)."
poetry run python -m thoughts.worker.main 