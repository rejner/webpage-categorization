FROM tensorflow/tensorflow:latest-gpu

# set working directory
# Application will be present in /workspace directory
WORKDIR /workspace/webcat

# install dependencies (requirements result in error)
# RUN pip install -r requirements.txt

RUN python3 -m pip install --upgrade pip
RUN pip install flask
RUN pip install flask-restful
RUN pip install flask-cors
RUN pip install flask-sqlalchemy
RUN pip install python-dotenv
RUN pip install urlextract
RUN pip install psycopg2-binary
RUN pip install beautifulsoup4
RUN pip install joblib
RUN pip install transformers
RUN pip install nltk
RUN pip install torch
RUN pip install datasets
RUN pip install openai==0.27.0

# expose port 5000
EXPOSE 5000

