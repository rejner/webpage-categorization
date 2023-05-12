FROM python:3.11-slim

# set working directory
WORKDIR /workspace/webcat

RUN python3 -m pip install --upgrade pip
RUN pip install flask
RUN pip install flask-restful
RUN pip install flask-cors
RUN pip install flask-sqlalchemy
RUN pip install psycopg2-binary
RUN pip install openai==0.27.0
RUN pip install beautifulsoup4
RUN pip install sentencepiece
RUN pip install nltk
RUN pip install debugpy
RUN pip install lxml

