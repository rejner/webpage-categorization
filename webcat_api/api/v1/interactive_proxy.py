from flask_restful import Resource, reqparse
from webcat.models_extension import *
import requests

# Requests for processing will have path to files, hypothesis template, labels and recursive flag + text
interactive_parser = reqparse.RequestParser()
interactive_parser.add_argument('hypothesis_template', type=str)
interactive_parser.add_argument('labels', type=str, action='append')
interactive_parser.add_argument('input', type=str)
interactive_parser.add_argument('models', type=str)

class WebCatInteractiveProxy(Resource):
    def __init__(self):
        super().__init__()

    def verify_interactive_request(self, args):
        if args['hypothesis_template'] is None or args['hypothesis_template'] == "":
            return False, "No hypothesis template provided"
        if args['labels'] is None or len(args['labels']) == 0 or args['labels'][0] == "":
            return False, "No labels provided"
        if args['input'] is None or args['input'] == "":
            return False, "No input text provided"
        return True, ""

    def get_available_worker(self, args):
        # construct request to webcat_scheduler
        # get free worker
        res = requests.post("http://webcat-scheduler:5001/webcat_scheduler", json=args)
        if res.status_code == 503:
            raise Exception("No available workers")
        
        available_worker = res.json()
        worker = available_worker['worker']
        return worker

    def release_worker(self, worker):
        # construct request to webcat_scheduler
        # release worker
        if worker is None:
            return
        res = requests.delete("http://webcat-scheduler:5001/webcat_scheduler", json=worker)
        if res.status_code != 200:
            raise Exception("Could not release worker")

    def get(self):
        return {'hello': 'world'}

    def post(self):
        # parse arguments in a form request
        args = interactive_parser.parse_args()
        # verify arguments
        valid, msg = self.verify_interactive_request(args)
        if not valid:
            return {'error': msg}, 400

        worker = None
        try:
            worker = self.get_available_worker(args)
            url = worker['url'] + "/webcat_interactive"
            res = requests.post(url, json=args)
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            self.release_worker(worker)
        
        return res.json(), res.status_code