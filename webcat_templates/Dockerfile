FROM ubuntu:20.04

# set working directory
# Application will be present in /workspace directory
WORKDIR /workspace/webcat

# install dependencies (requirements result in error)
# RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y software-properties-common gcc && \
    add-apt-repository -y ppa:deadsnakes/ppa

RUN apt-get update && apt-get install -y python3.10 python3-distutils python3-pip python3-apt

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

