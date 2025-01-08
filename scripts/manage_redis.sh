#!/bin/bash

# Function to restart Redis
restart_redis() {
    echo "Restarting Redis service..."
    sudo systemctl restart redis
}

# Function to check Redis status
check_redis_status() {
    echo "Checking Redis status..."
    sudo systemctl status redis --no-pager
}

# Function to flush Redis cache
flush_redis_cache() {
    echo "Purging Redis cache..."
    redis-cli FLUSHALL  # Use FLUSHDB if only the current DB needs clearing
}

# Main execution block
main() {
    echo "Managing Redis cache and service..."
    flush_redis_cache
    restart_redis
    check_redis_status
}

# Run the main function
main
