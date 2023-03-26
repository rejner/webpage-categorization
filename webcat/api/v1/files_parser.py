from flask_restful import Resource, reqparse
# from .worker import worker
from .worker import WebCatWorker
import logging
from database import db
from models_extension import *

files_parser = reqparse.RequestParser()
files_parser.add_argument('hypothesis_template', type=str)
files_parser.add_argument('labels', type=str, action='append')
files_parser.add_argument('path', type=str)
files_parser.add_argument('recursive', type=bool)

worker = WebCatWorker(db)

class WebCatFilesParser(Resource):
    def __init__(self):
        super().__init__()

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
        args = files_parser.parse_args()
        # verify arguments
        valid, msg = self.verify_request(args)
        if not valid:
            return {'error': msg}, 400

        try:
            contents, stats = worker.process_files(args['path'], 
                                        **{'hypothesis_template': args['hypothesis_template'], 
                                            'labels': args['labels'],
                                            'recursive': args['recursive']})
        except Exception as e:
            logging.error(e.with_traceback(None))
            return {'error': str(e)}, 400

        return {'contents': contents, 'stats': stats}, 200
        # return result, 200