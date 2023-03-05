# A simple flask RESTful API for the WebCat worker
# A React frontend will use this API to communicate with the worker

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from worker import WebCatWorker

# enable CORS for localhost
from flask_cors import CORS

worker = None

app = Flask(__name__)
# enable CORS for localhost
CORS(app)
api = Api(app)


# Requests for processing will have path to files, hypothesis template, labels and recursive flag + text
interactive_parser = reqparse.RequestParser()
interactive_parser.add_argument('hypothesis_template', type=str)
interactive_parser.add_argument('labels', type=str, action='append')
interactive_parser.add_argument('input', type=str)

files_parser = reqparse.RequestParser()
files_parser.add_argument('hypothesis_template', type=str)
files_parser.add_argument('labels', type=str, action='append')
files_parser.add_argument('path', type=str)
files_parser.add_argument('recursive', type=bool)


class WebCatInteractive(Resource):

    def verify_interactive_request(self, args):
        if args['hypothesis_template'] is None or args['hypothesis_template'] == "":
            return False, "No hypothesis template provided"
        if args['labels'] is None or len(args['labels']) == 0 or args['labels'][0] == "":
            return False, "No labels provided"
        if args['input'] is None or args['input'] == "":
            return False, "No input text provided"
        return True, ""

    def get(self):
        return {'hello': 'world'}

    def post(self):
        # parse arguments in a form request
        global worker
        args = interactive_parser.parse_args()
        # verify arguments
        valid, msg = self.verify_interactive_request(args)
        if not valid:
            return {'error': msg}, 400

        if worker is None:
            worker = WebCatWorker()
    
        result = worker.process_raw_text(args['input'], 
                                                   **{'hypothesis_template': args['hypothesis_template'], 
                                                    'labels': args['labels'],})
        
        return result, 200

class WebCatFilesParser(Resource):

    def verify_request(self, args):
        if args['hypothesis_template'] is None or args['hypothesis_template'] == "":
            return False, "No hypothesis template provided"
        if args['labels'] is None or len(args['labels']) == 0 or args['labels'][0] == "":
            return False, "No labels provided"
        if args['path'] is None or args['path'] == "":
            return False, "No path to input files provided"
        if args['recursive'] is None or args['recursive'] == "":
            return False, "No recursive flag provided"
        return True, ""

    def get(self):
        return {'hello': 'world'}

    def post(self):
        # parse arguments in a form request
        global worker
        args = files_parser.parse_args()
        # verify arguments
        valid, msg = self.verify_request(args)
        if not valid:
            return {'error': msg}, 400

        if worker is None:
            worker = WebCatWorker()
        try:
            result = worker.process_files(args['path'], 
                                        **{'hypothesis_template': args['hypothesis_template'], 
                                            'labels': args['labels'],
                                            'recursive': args['recursive']})
        except Exception as e:
            return {'error': str(e)}, 400
        
        return result, 200
        

api.add_resource(WebCatInteractive, '/api_v1/webcat_interactive')
api.add_resource(WebCatFilesParser, '/api_v1/webcat_files_parser')

if __name__ == '__main__':
    app.run(debug=True)
    



