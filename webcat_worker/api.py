from flask import Flask, current_app
from flask_restful import Api

from webcat.database import db
# enable CORS for localhost
from flask_cors import CORS

def create_app(host, port, bare=False):
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    # enable CORS for localhost
    CORS(app)
    db.init_app(app)
  
    if not bare:
        api = Api(app)
        from interactive import WebCatInteractive
        from files_parser import WebCatFilesParser

        api.add_resource(WebCatInteractive, '/webcat_interactive')
        api.add_resource(WebCatFilesParser, '/webcat_files_parser')

    # define ping route
    @app.route('/ping')
    def ping():
        return {'message': 'pong'}

    with app.app_context():
        db.create_all()

        from webcat.models_extension import Worker
        try:
            # get url of current running app
            url = 'http://{}:{}/'.format(host, port)
            worker = Worker.query.filter_by(url=url).first()
            if worker is None:
                worker = Worker(url=url, status='free', type='gpu')
                db.session.add(worker)
                db.session.commit()
        except Exception as e:
            print(e)
            exit(1)

    return app, db




