#!/bin/bash

# Run chmod 0644 for all files in /crons
chmod 0644 /crons/*
# Apply the cron job for all files in /crons
crontab /crons/*
# Create the log file to be able to run tail
touch /var/log/cron.log
# Run tail in the background to keep the container running
cron && tail -f /var/log/cron.log

