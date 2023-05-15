from flask_restful import Resource, reqparse, request
from flask import g
from webcat.pipeline import WebCatPipeline
import logging
from webcat.database import db
from webcat.models_extension import *
import os
from webcat.analyzer.models import list_all_models
import json

SUPPORTED_FILE_TYPES = ["csv", "html", "txt"]

pipeline = None

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

    def get(self):
        classification_models = [
            {
                "name": model['base_class'].name,
                "description": model['base_class'].description,
                "size": model['base_class'].size,
                "path": model['base_class'].path,
                "task": model['task'],
                "default": model['default'],
                "default_hypothesis": model['base_class'].default_hypothesis
            }
            for model in list_all_models() if model['task'] == "classification"
        ]
        ner_models = [
            {
                "name": model['base_class'].name,
                "description": model['base_class'].description,
                "size": model['base_class'].size,
                "path": model['base_class'].path,
                "task": model['task'],
                "default": model['default'],
            }
            for model in list_all_models() if model['task'] == "ner"
        ]

        presentation_models = json.dumps({
            "models": {
                "classification": classification_models,
                "ner": ner_models
            }
        })

        return presentation_models, 200
    
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
        
        models = args['models']

        try:
            global pipeline
            if pipeline is None or not pipeline.keep_cached_pipeline(models):
                pipeline = WebCatPipeline(db, models)
            
            file_paths = self.create_files_list(args['path'], recursive=args['recursive'])
            contents, stats = pipeline.process_files_as_dataset(file_paths, **args)

        except Exception as e:
            logging.error(e.with_traceback(None))
            return {'error': str(e)}, 400

        return {'contents': contents, 'stats': stats}, 200
