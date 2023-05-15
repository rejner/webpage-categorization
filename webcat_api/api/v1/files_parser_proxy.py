import os
import json
import requests
from flask_restful import Resource, reqparse, request
import logging
from webcat.models_extension import *

SUPPORTED_FILE_TYPES = ["csv", "html", "txt"]

class WebCatFilesParserProxy(Resource):
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

    def create_files_list(self, path:str, **kwargs):
        logging.info("Creating files list from path: {}".format(path))
        recursive = kwargs.get("recursive", False)
        # if path is a file, return it
        if os.path.isfile(path):
            return [path]
        
        # if path is a directory, return all files in it
        # if recursive is True, return all files in all subdirectories
        files = []
        if os.path.isdir(path):
            if not recursive:
                for filename in os.listdir(path):
                    file_path = os.path.join(path, filename)
                    if os.path.isfile(file_path):
                        files.append(file_path)
            else:
                for root, dirs, files in os.walk(path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        files.append(file_path)

            logging.info("Found {} files in path: {}".format(len(files), path))
            return files
        
        raise Exception("Path is not a file or directory")

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

    # retrieve all available models
    def get(self):
        # get available worker
        workers = requests.get("http://webcat-scheduler:5001/webcat_scheduler")
        worker = workers.json()['workers'][0]
        try:
            # send request to worker to get available models
            url = worker['url'] + "/webcat_files_parser"
            res = requests.get(url)
        except Exception as e:
            logging.error(e.with_traceback(None))
            return {'error': str(e)}, 400
        
        return res.json(), 200
    
    def post(self):
        # parse arguments in a form request
        args = request.get_json(force=True)
        # verify arguments
        valid, msg = self.verify_request(args)
        if not valid:
            return {'error': msg}, 400

        # get file type
        file_type = args['file_type']
        if file_type not in SUPPORTED_FILE_TYPES:
            return {'error': "File type not supported"}, 400

        worker = None
        try:
            worker = self.get_available_worker(args)
            url = worker['url'] + "/webcat_files_parser"
            res = requests.post(url, json=args)
        except Exception as e:
            logging.error(e.with_traceback(None))
            return {'error': str(e)}, 400
        finally:
            self.release_worker(worker)

        return res.json(), res.status_code