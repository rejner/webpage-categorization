from flask_restful import Resource, reqparse, request
from webcat.models_extension import *
import requests

# Sending requests to webcat_tempaltes service
class WebCatTempaltesProxy(Resource):
    def __init__(self):
        super().__init__()

    def get(self):
        res = requests.get("http://webcat-templates:5002/templates")
        return res.json(), res.status_code

    def post(self):
        res = requests.post("http://webcat-templates:5002/templates", json=request.json)
        return res.json(), res.status_code
    
    def delete(self):
        res = requests.delete("http://webcat-templates:5002/templates", json=request.json)
        return res.json(), res.status_code
    