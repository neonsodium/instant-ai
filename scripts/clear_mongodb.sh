#!/bin/bash

# Configuration
MONGO_HOST="localhost"
MONGO_PORT="27017"
DATABASE_NAME="instant_ai"
COLLECTION_NAME="projects"

echo "Select an option to clear MongoDB data:"
echo "1. Clear all documents from a specific collection"
echo "2. Drop a specific collection"
echo "3. Drop the entire database"
read -p "Enter your choice (1/2/3): " CHOICE

case $CHOICE in
  1)
    echo "Clearing all documents from collection: $COLLECTION_NAME in database: $DATABASE_NAME"
    mongosh --host $MONGO_HOST --port $MONGO_PORT $DATABASE_NAME --eval "db.$COLLECTION_NAME.deleteMany({})"
    echo "All documents have been cleared from the collection."
    ;;
  2)
    echo "Dropping collection: $COLLECTION_NAME from database: $DATABASE_NAME"
    mongosh --host $MONGO_HOST --port $MONGO_PORT $DATABASE_NAME --eval "db.$COLLECTION_NAME.drop()"
    echo "The collection has been dropped."
    ;;
  3)
    echo "Dropping the entire database: $DATABASE_NAME"
    mongosh --host $MONGO_HOST --port $MONGO_PORT --eval "db.getSiblingDB('$DATABASE_NAME').dropDatabase()"
    echo "The database has been dropped."
    ;;
  *)
    echo "Invalid choice. Exiting."
    ;;
esac
