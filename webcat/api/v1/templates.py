from flask_restful import Resource, reqparse, request
import json
from os import path
from database import db
from models_extension import *
import logging
from nlp.processing.template_engine import list_engines

class WebCatTemplates(Resource):
    def __init__(self):
        super().__init__()
        self.element_types = self.fetch_element_types()
        self.element_type_to_id = {element_type.name: element_type.id for element_type in self.element_types}
        if len(self.element_types) == 0:
            self.create_default_element_types()
            self.element_types = self.fetch_element_types()

    def fetch_element_types(self):
        element_types = db.session.query(ElementType_v2).all()
        return element_types

    def create_default_element_types(self):
        """
            Create default element types.
        """
        element_types = ['post-message', 'post-author', 'post-header']
        for element_type in element_types:
            new_element_type = ElementType_v2(element_type)
            db.session.add(new_element_type)
        db.session.commit()

    def get_manager(self):
        # get version from URL parameter
        data = request.args
        version = int(data['version'])
        if 'version' not in data:
            return {'error': "No version specified"}, 400
        
        if version == 1:
            templates = db.session.query(Template).all()
            templates = [template.json_serialize() for template in templates]
            res = json.dumps(templates)
        
        if version == 2:
            templates = db.session.query(Template_v2).all()
            templates = [template.json_serialize() for template in templates]
            res = json.dumps(templates)

        return res, 200

    def get_engine(self):
        """
            List all available engines.
        """
        engines = list_engines()
        payload = [{'name': engine.name, 'description': engine.description, 'requiresKey': engine.requiresKey} for engine in engines]
        return json.dumps(payload), 200

    def get(self, service):
        if service == 'manager':
            return self.get_manager()
        
        if service == 'engine':
            return self.get_engine()
        
        return {'error': "No such service"}, 400
        
    def create_template_v1(self, data):
        newTemplate = Template(data['creation_date'], data['origin_file'])
        newElements = []
        for element in data['elements']:
            newElements.append(Element(element['tag'], element['classes'], element['id_attr'], element['type']))
        newTemplate.elements = newElements

        db.session.add(newTemplate)
        db.session.commit()
        return {'id': newTemplate.id}, 200
    
    def create_template_v2(self, data):
        newTemplate = Template_v2(data['creation_date'], data['origin_file'])
        newElements = []
        for element in data['elements']:
            newElements.append(Element_v2(element['tag'], self.element_type_to_id[element['type']], element['parent_tag'], element['grandparent_tag'], element['depth']))
        newTemplate.elements = newElements

        db.session.add(newTemplate)
        db.session.commit()
        payload = json.dumps(str({'id': newTemplate.id}))
        return payload, 200

    def creator_post(self):
        try:
            # get template object from request
            data = request.get_json()
            if not 'version' in data.keys():
                return {'error': "No version specified"}, 400
            
            if data['version'] == 1:
                return self.create_template_v1(data['template'])
            if data['version'] == 2:
                return self.create_template_v2(data['template'])
            else:
                return {'error': "No such version"}, 400

        except Exception as e:
            return {'error': str(e)}, 400
    
    def engine_post(self):
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

    def post(self, service):
        if service == 'manager':
            return self.creator_post()
        
        if service == 'engine':
            return self.engine_post()

    def put(self, service):
        if service != 'manager':
            return {'error': "Invalid service"}, 400
        
        pass
    
    # delete will be sent as a delete request with id in the url
    def delete(self, service):
        if service != 'manager':
            return {'error': "Invalid service"}, 400
        
        id = request.json['id']
        version = request.json['version']
        if id is None:
            return {'error': "No id provided"}, 400
        try:
            if version == 1:
                template = db.session.query(Template).get(id)
            if version == 2:
                template = db.session.query(Template_v2).get(id)
            db.session.delete(template)
            db.session.commit()
        except Exception as e:
            return {'error': str(e)}, 400
        
        return "Success", 200