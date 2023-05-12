from flask_restful import Resource, reqparse, request
from webcat.models_extension import *
import requests

class WebCatTempaltesEngineProxy(Resource):
    def __init__(self):
        super().__init__()

    def get(self):
        res = requests.get("http://webcat-templates:5002/engine")
        return res.json(), res.status_code

    def post(self):
        res = requests.post("http://webcat-templates:5002/engine", json=request.json)
        return res.json(), res.status_code

    