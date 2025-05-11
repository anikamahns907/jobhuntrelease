#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Copy the plist file to LaunchAgents directory
cp com.jobhuntrelease.plist ~/Library/LaunchAgents/

# Load the service
launchctl load ~/Library/LaunchAgents/com.jobhuntrelease.plist

echo "Service installed and started!"
echo "To check status: launchctl list | grep jobhuntrelease"
echo "To stop service: launchctl unload ~/Library/LaunchAgents/com.jobhuntrelease.plist"
echo "To start service: launchctl load ~/Library/LaunchAgents/com.jobhuntrelease.plist"
echo "Logs will be written to error.log and output.log in the current directory" 