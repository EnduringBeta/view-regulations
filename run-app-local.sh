#!/bin/bash

if [ -z "$1" ]; then
  echo "Database password required"
  exit 1
fi

MYSQL_PASSWORD="$1"

echo "Starting View Regulations Web App..."

# Assuming in proper working directory

echo "Checking MySQL is available..."

mysql --version

# Start MySQL in background and run initial SQL script to create database and user
mysql -u root -p$MYSQL_PASSWORD < init.sql

# Activate Python virtual environment, which is assumed to have been set up parallel to repo
. myenv/bin/activate

# .env environment variables are set in Python using `load_dotenv`

# Run the API (in background with "&")!
# Use host arg for all addresses
flask --app api/app.py run &
#flask --app api/app.py run --host=0.0.0.0 --port=5000 &
#python3 app.py

echo "Pausing for any API messages..."

sleep 3

# Run the UI!
cd ui/ && npm start

echo "Ending View Regulations Web App..."
