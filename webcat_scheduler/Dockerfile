FROM python:3.11-slim

# Application will be present in /workspace directory
WORKDIR /workspace/webcat

RUN python3 -m pip install --upgrade pip
RUN pip install flask
RUN pip install flask-restful
RUN pip install flask-cors
RUN pip install flask-sqlalchemy
RUN pip install psycopg2-binary
RUN pip install debugpy
RUN pip install requests


