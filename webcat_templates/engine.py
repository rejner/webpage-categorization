from flask_restful import Resource, reqparse, request
import json
from os import path
from webcat.database import db
from webcat.models_extension import *
import logging
from webcat.template_engine import list_engines

class WebCatTemplatesEngine(Resource):
    def __init__(self):
        super().__init__()

    def get(self):
        """
            List all available engines.
        """
        engines = list_engines()
        payload = [{'name': engine.name, 'description': engine.description, 'requiresKey': engine.requiresKey} for engine in engines]
        return json.dumps(payload), 200

    def post(self):
        """
        This is the post request for the engine service.
        Engine service automatically creates a template from the file.
        """
        try:
            data = request.get_json()
            model = data['model']
            file = data['file_path']
            key = data['key']
            engines = list_engines()
            engine = next(filter(lambda x: x.name == model, engines), None)
            if engine is None:
                return {'error': "No such engine"}, 400
            
            if engine.requiresKey and key is None:
                return {'error': "Engine requires key"}, 400
            
            if not path.exists(file):
                return {'error': "File does not exist"}, 400
            
            if engine.requiresKey:
                engine.setKey(key)
            
            try:  
                proposal, (response, prompt, total_tokens) = engine.template_from_file(file)
            except Exception as e:
                logging.warn(f"Error while creating template from file: {e}")
                return {'error': "Error while creating template from file", 
                        'response': response,
                        'prompt': prompt,
                        'total_tokens': total_tokens}, 400

            # logging.warn(f"Received request for template creation from engine service. Model: {model}, file: {file}, key: {key}")
            if proposal is None:
                return {'error': "Template creation was not successful.",
                        'response': response,
                        'prompt': prompt,
                        'total_tokens': total_tokens
                        }, 400

        except Exception as e:
            return {'error': str(e)}, 400
        
        return json.dumps({
            'template': proposal,
            'response': response,
            'prompt': prompt,
            'total_tokens': total_tokens
        }), 200
