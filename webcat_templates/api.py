from flask import Flask
from flask_restful import Api
from webcat.database import db
# enable CORS for localhost
from flask_cors import CORS

def create_app(bare=False):
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    # enable CORS for localhost
    CORS(app)
    db.init_app(app)
    
    if not bare:
        api = Api(app)
        from element_types import WebCatElementTypes
        from templates import WebCatTemplates
        from engine import WebCatTemplatesEngine
        api.add_resource(WebCatElementTypes, '/element_types')
        api.add_resource(WebCatTemplates, '/templates')
        api.add_resource(WebCatTemplatesEngine, '/engine')
    
    # define ping route
    @app.route('/ping')
    def ping():
        return {'message': 'pong'}

    with app.app_context():
        db.create_all()

    return app, db

    



