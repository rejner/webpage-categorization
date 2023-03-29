from flask_restful import Resource, reqparse, request
import json
from os import path
from database import db
from models_extension import *

class WebCatTemplateCreator(Resource):
    def __init__(self):
        super().__init__()

    def get(self):
        # return template_storage
        templates = db.session.query(Template).all()
        templates = [template.json_serialize() for template in templates]
        res = json.dumps(templates)
        return res, 200 

    def post(self):
        try:
            # get template object from request
            data = request.get_json()
            newTemplate = Template(data['creation_date'], data['origin_file'])
            newElements = []
            for element in data['elements']:
                newElements.append(Element(element['tag'], element['classes'], element['id_attr'], element['type']))
            newTemplate.elements = newElements

            db.session.add(newTemplate)
            db.session.commit()

        except Exception as e:
            return {'error': str(e)}, 400
        
        return "Success", 200

    def put(self):
        pass
    
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