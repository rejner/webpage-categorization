# A simple flask RESTful API for the WebCat worker
# A React frontend will use this API to communicate with the worker
from flask import Flask
from flask_restful import Api

from database import db
# enable CORS for localhost
from flask_cors import CORS

def create_app(bare=False):
    app = Flask(__name__)
    app.config.from_envvar('FLASK_CONFIG')
    # enable CORS for localhost
    CORS(app)
    db.init_app(app)
    
    if not bare:
        api = Api(app)
        from api.v1.interactive import WebCatInteractive
        from api.v1.files_parser import WebCatFilesParser
        from api.v1.templates import WebCatTemplates
        from api.v1.data_provider import WebCatDataProvider

        api.add_resource(WebCatInteractive, '/api/v1/webcat_interactive')
        api.add_resource(WebCatFilesParser, '/api/v1/webcat_files_parser')
        api.add_resource(WebCatTemplates, '/api/v1/webcat_templates/<string:service>')
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
    



