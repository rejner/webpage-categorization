from flask_restful import Resource, reqparse
from flask import current_app
# from .worker import worker
from database import db
from models_extension import *
# from .worker import WebCatWorker
from nlp.pipeline import WebCatPipeline
import json

# Requests for processing will have path to files, hypothesis template, labels and recursive flag + text
interactive_parser = reqparse.RequestParser()
interactive_parser.add_argument('hypothesis_template', type=str)
interactive_parser.add_argument('labels', type=str, action='append')
interactive_parser.add_argument('input', type=str)
interactive_parser.add_argument('models', type=str)

class WebCatInteractive(Resource):
    def __init__(self):
        super().__init__()
        # self.worker = WebCatWorker(db)
        self.pipeline = None

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
        args = interactive_parser.parse_args()
        # verify arguments
        valid, msg = self.verify_interactive_request(args)
        if not valid:
            return {'error': msg}, 400

        # get models
        models = args['models']
        models = json.loads(models)

        if not self.pipeline:
            self.pipeline = WebCatPipeline(db, models)

        result = self.pipeline.process_raw_text(args['input'],**{'hypothesis_template': args['hypothesis_template'], 
                                                        'labels': args['labels'],})

        # result = self.worker.process_raw_text(args['input'], 
        #                                             **{'hypothesis_template': args['hypothesis_template'], 
        #                                                 'labels': args['labels'],})
        
        return result, 200