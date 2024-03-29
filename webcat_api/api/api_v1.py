# A simple flask RESTful API for the WebCat worker
# A React frontend will use this API to communicate with the worker
from flask import Flask, g
from flask_restful import Api
import requests
from datetime import datetime

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
        from api.v1.interactive_proxy import WebCatInteractiveProxy
        from api.v1.files_parser_proxy import WebCatFilesParserProxy
        from api.v1.data_provider import WebCatDataProvider
        from api.v1.templates_engine_proxy import WebCatTempaltesEngineProxy
        from api.v1.templates_element_types_proxy import WebCatTempaltesElementTypesProxy
        from api.v1.templates_proxy import WebCatTempaltesProxy

        api.add_resource(WebCatInteractiveProxy, '/api/v1/webcat_interactive')
        api.add_resource(WebCatFilesParserProxy, '/api/v1/webcat_files_parser')
        api.add_resource(WebCatTempaltesEngineProxy, '/api/v1/webcat_templates/engine')
        api.add_resource(WebCatTempaltesElementTypesProxy, '/api/v1/webcat_templates/element_types')
        api.add_resource(WebCatTempaltesProxy, '/api/v1/webcat_templates/templates')
        api.add_resource(WebCatDataProvider, '/api/v1/webcat_data_provider')
    
    # define ping route
    @app.route('/api/v1/ping')
    def ping():
        return {'message': 'pong'}

    with app.app_context():
        db.create_all()

    return app, db

if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    app, _ = create_app('config.py')
    # set module
    
    app.run(debug=True)
    



