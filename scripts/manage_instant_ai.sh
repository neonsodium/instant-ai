#!/bin/bash

# Define paths and constants
REQUIREMENTS_FILE="/home/ubuntu/instant-ai/requirements.txt"
SERVICE1="instant-ai.service"
SERVICE2="instant-ai-celery.service"
CACHE_REDIS_SCRIPT="/home/ubuntu/cache_redis.sh"
PURGE_REDIS_SCRIPT="/home/ubuntu/purge_cache_redis.sh"

# Function to install dependencies
install_dependencies() {
    echo "Installing dependencies..."
    pip3 install --break-system-packages -r $REQUIREMENTS_FILE
}

# Function to reload and stop services
reload_and_stop_services() {
    echo "Reloading and stopping services..."
    sudo systemctl daemon-reload
    sudo systemctl stop $SERVICE1
    sudo systemctl stop $SERVICE2
}

# Function to enable services
enable_services() {
    echo "Enabling services..."
    sudo systemctl enable $SERVICE1
    sudo systemctl enable $SERVICE2
}

# Function to start services
start_services() {
    echo "Starting services..."
    sudo systemctl start $SERVICE2
    sudo systemctl start $SERVICE1
}

# Function to check service statuses
check_service_status() {
    echo "Checking service statuses..."
    sudo systemctl status $SERVICE1
    sudo systemctl status $SERVICE2
}

# Function to handle Redis cache scripts
handle_redis_cache() {
    echo "Running Redis cache scripts..."
    $CACHE_REDIS_SCRIPT
    $PURGE_REDIS_SCRIPT
}

# Main execution block
main() {
    install_dependencies
    reload_and_stop_services
    enable_services
    start_services
    check_service_status
    handle_redis_cache
}

# Run the main function
main
