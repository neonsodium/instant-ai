#!/bin/bash

# Function to clean up processes
cleanup() {
    echo "Cleaning up processes..."
    kill $REDIS_PID $CELERY_PID $FLASK_PID
    exit
}

# Trap to handle script termination
trap cleanup SIGINT SIGTERM

# Start Redis server
echo "Starting Redis..."
redis-server &  # Start in the background
REDIS_PID=$!

# Start Celery worker
echo "Starting Celery..."
celery -A celery_worker.celery worker --loglevel=INFO &  # Start in the background
CELERY_PID=$!

# Start Flask app using python3
echo "Starting Flask app..."
python3 run.py &  # Start in the background
FLASK_PID=$!

# Wait for all processes to complete
wait

#!/bin/bash

# # Function to clean up processes
# cleanup() {
#     echo "Cleaning up processes..."
#     kill $REDIS_PID $CELERY_PID $FLASK_PID
#     exit
# }

# # Trap to handle script termination
# trap cleanup SIGINT SIGTERM

# # Start Redis server and redirect output
# echo "Starting Redis..."
# redis-server > redis.log 2>&1 &
# REDIS_PID=$!

# # Start Celery worker and redirect output
# echo "Starting Celery..."
# celery -A celery_worker.celery worker --loglevel=info > celery.log 2>&1 &
# CELERY_PID=$!

# # Start Flask app using python3 and redirect output
# echo "Starting Flask app..."
# python3 run.py > flask.log 2>&1 &
# FLASK_PID=$!

# # Wait for all processes to complete
# wait
