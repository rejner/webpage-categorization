#!/bin/bash
# This script is used to run WebCat system on any machine with GPU (NVIDIA CUDA).
# It is recommended to use GPU as it provides much faster inference times.

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found, cloning from .env.example"
    cp .env.example .env
fi

# Check if .env file is writable
if [ ! -w .env ]; then
    echo "Error: .env file is not writable"
    exit 1
fi

# Set variables
PWD=$(pwd)
LOCAL_PATH="$PWD"
SERVER_IP=$(grep SERVER_IP .env | cut -d= -f2)
echo "SERVER_IP=$SERVER_IP"
echo "LOCAL_PATH=$LOCAL_PATH"

# Update LOCAL_PATH variable
sed "s|LOCAL_PATH=.*|LOCAL_PATH=$LOCAL_PATH|g" .env > .env.tmp
mv .env.tmp .env

# Update SERVER_IP variable
sed "s|SERVER_IP=.*|SERVER_IP=$SERVER_IP|g" .env > .env.tmp
mv .env.tmp .env

# distribute config.py to all services
cp config.py ./webcat_api/config.py
cp config.py ./webcat_worker/config.py
cp config.py ./webcat_scheduler/config.py
cp config.py ./webcat_templates/config.py

# due to some metadata issues, we have to pull dependant images manually
docker pull python:3.11-slim
docker pull nginx:1.21.0-alpine
docker pull node:16-alpine

# run docker-compose
docker-compose -p webcat_gpu_prod -f docker-compose.gpu.yaml up -d

