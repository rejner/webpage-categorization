# A simple flask RESTful API for the WebCat worker
# A React frontend will use this API to communicate with the worker
from flask import Flask
from flask_restful import Api
from db_models.category import Category
from db_models.content import Content
from db_models.file import File
from db_models.named_entity import NamedEntity, EntityType
from db_models.content_category import ContentCategory
from db_models.content_entity import ContentEntity
from database import init_db, db
# enable CORS for localhost
from flask_cors import CORS

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)
    # enable CORS for localhost
    CORS(app)
    db = init_db(app)
    api = Api(app)

    from api.v1.interactive import WebCatInteractive
    from api.v1.files_parser import WebCatFilesParser
    from api.v1.templates import WebCatTemplates

    api.add_resource(WebCatInteractive, '/api/v1/webcat_interactive')
    api.add_resource(WebCatFilesParser, '/api/v1/webcat_files_parser')
    api.add_resource(WebCatTemplates, '/api/v1/webcat_templates')

    return app, db

if __name__ == '__main__':
    app, _ = create_app('config.py')
    app.run(debug=True)
    



