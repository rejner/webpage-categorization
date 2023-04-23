from flask_restful import Resource, reqparse, request
import json
from os import path
from webcat.database import db
from webcat.models_extension import *
import logging
from webcat.template_engine import list_engines
import requests

class WebCatTemplates(Resource):
    def __init__(self):
        super().__init__()
    
    def search_for_element_type(self, tag):
        logging.info(f"Searching for element type with tag {tag}")
        el_type = db.session.query(ElementType).filter(ElementType.tag == tag).first()
        logging.info(f"Found element type: {el_type}")
        if el_type is None:
            return None
        return el_type.json_serialize()

    def create_template(self, data):
        newTemplate = Template(data['creation_date'], data['origin_file'])
        newElements = []
        for element in data['elements']:
            if isinstance(element['type'], str):
                element['type'] = self.search_for_element_type(element['type'])
            newElements.append(Element(element['tag'], element['type']['id'], element['parent_tag'], element['grandparent_tag'], element['depth']))
        newTemplate.elements = newElements

        db.session.add(newTemplate)
        db.session.commit()
        payload = json.dumps(str({'id': newTemplate.id}))
        return payload, 200


    def get(self):
        templates = db.session.query(Template).all()
        templates = [template.json_serialize() for template in templates]
        res = json.dumps(templates)

        return res, 200

    def post(self):
        try:
            # get template object from request
            data = request.get_json()
            logging.info(f"POST request received: {data}")
            return self.create_template(data['template'])

        except Exception as e:
            logging.error(e)
            return {'error': str(e)}, 400

    
    # delete will be sent as a delete request with id in the url
    def delete(self):
        id = request.json['id']
        if id is None:
            return {'error': "No id provided"}, 400
        try:

            template = db.session.query(Template).get(id)
            db.session.delete(template)
            db.session.commit()
        except Exception as e:
            return {'error': str(e)}, 400
        
        return "Success", 200