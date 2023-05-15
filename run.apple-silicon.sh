#!/bin/bash
# This script is used to run WebCat system on Apple Silicon (M1) machines.
# The worker service is run outside of docker container, because it is not possible to run
# PyTorch with MPS backend inside of container yet.
# It is assumed that docker is already installed on the machine.

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

# docker-compose
docker-compose -p webcat_apple-silicon_prod -f docker-compose.apple-silicon.yaml up -d

# Worker has to be started and installed locally on Apple machine in order to make MPS backend work

# create python virtual environment
python3 -m venv venv

# activate virtual environment
source venv/bin/activate


# install requirements
# check if packages are installed correctly
pip3 install flask
pip3 install flask-restful
pip3 install flask-cors
pip3 install flask-sqlalchemy
pip3 install python-dotenv
pip3 install urlextract
pip3 install psycopg2-binary
pip3 install beautifulsoup4
pip3 install joblib
pip3 install transformers
pip3 install nltk
pip3 install --default-timeout=100 torch
pip3 install datasets
pip3 install openai==0.27.0
pip3 install sentencepiece
pip3 install protobuf==3.20.0
pip3 install datefinder
pip3 install debugpy
pip3 install lxml
pip install urllib3==1.26.6

# set environment variables
export PORT=5003
export HOST=docker.for.mac.localhost

# distribute config.py to all services
cp config.py ./webcat_api/config.py
cp config.py ./webcat_worker/config.py
cp config.py ./webcat_scheduler/config.py
cp config.py ./webcat_templates/config.py

# update SQL_HOST variable in webcat_worker/config.py to localhost (for Apple Silicon),
# because worker must run outside of docker container on Apple Silicon and can connect
# to database only via localhost
echo "Updating SQL_HOST variable in webcat_worker/config.py to localhost"
sed "s|SQL_HOST = .*|SQL_HOST = \"localhost\"|g" webcat_worker/config.py > webcat_worker/config.tmp
mv webcat_worker/config.tmp webcat_worker/config.py

# run worker
python3 webcat/model_repository/download.py
python3 webcat_worker/run.py
