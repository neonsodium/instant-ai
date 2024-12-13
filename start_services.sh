#!/bin/bash


cleanup() {
    echo "Cleaning up processes..."
    kill $REDIS_PID $CELERY_PID $FLASK_PID
    exit
}

# Trap to handle script termination
trap cleanup SIGINT SIGTERM


echo "Starting Redis..."
redis-server &
REDIS_PID=$!


echo "Starting Celery..."
celery -A celery_worker.celery worker --loglevel=INFO &  
CELERY_PID=$!

echo "Starting Flask app..."
python3 run.py &  
FLASK_PID=$!

# Wait for all processes to complete
wait
