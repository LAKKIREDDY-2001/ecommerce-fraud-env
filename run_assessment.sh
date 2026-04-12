#!/usr/bin/env bash

echo "Starting the support triage environment server..."
# Start the server in the background
uv run server &
SERVER_PID=$!

# Wait a few seconds for the server to fully start
sleep 3

echo "Server started. Running assessment inference..."
# Output the result of the local baseline
ENV_URL=http://localhost:7860 uv run python inference.py

echo "Assessment complete! Output saved to assessment_output.json."

echo "Cleaning up server..."
kill -9 $SERVER_PID 2>/dev/null || true
