from flask_restful import Resource, reqparse, request
import json
from os import path
from webcat.database import db
from webcat.models_extension import *
from const import DEFAULT_ELEMENT_TYPES

class WebCatElementTypes(Resource):
    def __init__(self):
        super().__init__()
        self.element_types = self.fetch_element_types()
        self.element_type_to_id = {element_type.name: element_type.id for element_type in self.element_types}
        if len(self.element_types) == 0:
            self.create_default_element_types()
            self.element_types = self.fetch_element_types()

    def fetch_element_types(self):
        element_types = db.session.query(ElementType).all()
        return element_types

    def create_default_element_types(self):
        """
            Create default element types.
        """
        for element_type in DEFAULT_ELEMENT_TYPES:
            new_element_type = ElementType(element_type['name'], element_type['tag'], element_type['analysis_flag'])
            db.session.add(new_element_type)
        db.session.commit()

    def create_element_type(self, data):
        new_element_type = ElementType(data['name'], data['tag'], data['analysis_flag'])
        db.session.add(new_element_type)
        db.session.commit()
        payload = json.dumps(str({'id': new_element_type.id}))
        return payload, 200


    def get(self):
        element_types = db.session.query(ElementType).all()
        element_types = [element_type.json_serialize() for element_type in element_types]
        res = json.dumps(element_types)

        return res, 200
    

    def post(self):
        try:
            # get template object from request
            data = request.get_json()
            if not 'version' in data.keys():
                return {'error': "No version specified"}, 400
        
            return self.create_element_type(data)

        except Exception as e:
            return {'error': str(e)}, 400

    
    # delete will be sent as a delete request with id in the url
    def delete(self):
        id = request.json['id']
        if id is None:
            return {'error': "No id provided"}, 400
        try:

            element_type = db.session.query(ElementType).get(id)
            db.session.delete(element_type)
            db.session.commit()
            
        except Exception as e:
            return {'error': str(e)}, 400
        
        return "Success", 200