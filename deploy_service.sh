#!/bin/bash

# Define variables
SERVICE_FILE="deploy/messageapp.service"
SYSTEMD_DIR="/etc/systemd/system"
SERVICE_NAME="messageapp.service"

echo "Deploying $SERVICE_NAME..."

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "Error: Service file $SERVICE_FILE not found!"
    exit 1
fi

# Copy service file to systemd directory
echo "Copying service file to $SYSTEMD_DIR..."
sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/"

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service
echo "Enabling $SERVICE_NAME..."
sudo systemctl enable "$SERVICE_NAME"

# Restart the service
echo "Restarting $SERVICE_NAME..."
sudo systemctl restart "$SERVICE_NAME"

# Check status
echo "Checking service status..."
sudo systemctl status "$SERVICE_NAME" --no-pager

echo "Deployment complete!"
