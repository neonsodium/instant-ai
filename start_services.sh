#!/bin/bash

# Start Redis server
echo "Starting Redis..."
redis-server &

# Start Celery worker
echo "Starting Celery..."
celery -A celery_worker.celery worker --loglevel=info &

# Start Flask server
echo "Starting Flask..."
export FLASK_APP=run.py
python3 run.py
