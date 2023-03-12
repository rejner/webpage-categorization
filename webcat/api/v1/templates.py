from flask_restful import Resource, reqparse
import json
from os import path

templates = reqparse.RequestParser()
templates.add_argument('templates', type=str)

class WebCatTemplates(Resource):
    def __init__(self):
        super().__init__()
        # load json from file
        self.storage_path = path.dirname(__file__) + '/../storage/templates.json'
        self.template_storage = json.load(open(self.storage_path, 'r'))

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
        return json.dumps(self.template_storage), 200
    

    def post(self):
        # parse arguments in a form request
        args = templates.parse_args()
        # verify arguments
        valid, msg = self.verify_request(args)
        if not valid:
            return {'error': msg}, 400
        
        # templates should be a list of objects with the following fields:
        # - type    (str)
        # - tag     (str)
        # - id      (str)
        # - classes (list)

        written = False
        for template in json.loads(args['templates']):
            print(template)
            if not template in self.template_storage[template['type']]:
                print("Template not in storage, adding...")
                self.template_storage[template['type']].append(template)
                written = True
        
        if written:
            with open(self.storage_path, 'w') as f:
                json.dump(self.template_storage, f)
            
        
        return "Success", 200