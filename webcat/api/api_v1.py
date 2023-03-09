# A simple flask RESTful API for the WebCat worker
# A React frontend will use this API to communicate with the worker
from flask import Flask, request
from flask_restful import Api
from api.v1.interactive import WebCatInteractive
from api.v1.files_parser import WebCatFilesParser
from api.v1.templates import WebCatTemplates


# enable CORS for localhost
from flask_cors import CORS

worker = None

app = Flask(__name__)
# enable CORS for localhost
CORS(app)
api = Api(app)

api.add_resource(WebCatInteractive, '/api/v1/webcat_interactive')
api.add_resource(WebCatFilesParser, '/api/v1/webcat_files_parser')
api.add_resource(WebCatTemplates, '/api/v1/webcat_templates')

if __name__ == '__main__':
    app.run(debug=True)
    



