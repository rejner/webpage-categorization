from flask import Flask
import os
import sys
# append path ../webcat to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webcat.models_extension import *
from webcat.database import db

# create a flask app context
app = Flask(__name__)
app.config.from_pyfile('../config.py')
db.init_app(app)

def drop_database():
    db.drop_all()

if __name__ == '__main__':
    with app.app_context():
        drop_database()

