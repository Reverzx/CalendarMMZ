#!/bin/bash

echo "Starting Calendar Application..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit .env file and add your TELEGRAM_BOT_TOKEN!"
    echo "Opening .env file..."
    ${EDITOR:-nano} .env
fi

echo "Building and starting Docker containers..."
docker-compose up -d --build

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "Calendar Application started successfully!"
    echo "========================================="
    echo ""
    echo "Web interface: http://localhost:5000"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "To stop:"
    echo "  docker-compose down"
    echo ""
else
    echo ""
    echo "ERROR: Failed to start containers!"
    echo "Please check Docker is running and try again."
    exit 1
fi
