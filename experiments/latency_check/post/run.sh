#!/bin/bash

# Shell script to start FastAPI server and run the client-side latency test

# Function to start the FastAPI server
start_server() {
  echo "Starting FastAPI server..."
  python3 server.py &
  SERVER_PID=$!
  sleep 3  # Wait for the server to start
}

# Function to run the client-side latency test
run_client() {
  echo "Running client-side latency test..."
  python3 client.py
}

# Function to stop the FastAPI server
stop_server() {
  echo "Stopping FastAPI server..."
  kill $SERVER_PID
}

# Start the server
start_server

# Run the client
run_client

# Stop the server
stop_server

echo "Latency test completed."
