from flask_restful import Resource, reqparse, request
import json
from os import path

from api.repositories.templates import TemplatesRepository, Template, TemplateEncoder
from database import db
from db_models.element import Element
from db_models.template_element import TemplateElement
from db_models.template import Template


class WebCatTemplates(Resource):
    def __init__(self):
        super().__init__()

    def verify_request(self, args):
        if args['templates'] is None or args['templates'] == "":
            return False, "No template provided"
        try:
            templates_list = json.loads(args['templates'])
        except Exception as e:
            return False, "Invalid template format"
        
        if not isinstance(templates_list, list):
            return False, "Invalid template format"

        return True, ""

    def get(self):
        # return template_storage
        return json.dumps(self.repository.get_all(), cls=TemplateEncoder), 200    

    def post(self):
        # parse arguments in a form request
        # args = templates.parse_args()
        # # verify arguments
        # valid, msg = self.verify_request(args)
        # if not valid:
        #     return {'error': msg}, 400

        # get template object from request
        data = request.get_json()
        # convert to template object
        template = Template.from_json(data)
        print(template)
        # # add template to storage
        newTemplate = self.repository.create(template)
        if newTemplate is None:
            return {'error': "Template could not be created"}, 400
        
        return "Success", 200

    def put(self):
        pass
    
    # delete will be sent as a delete request with id in the url
    def delete(self):
        id = request.json['id']
        if id is None:
            return {'error': "No id provided"}, 400
        self.repository.delete(id)
        return "Success", 200