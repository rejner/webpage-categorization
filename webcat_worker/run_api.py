import os
import logging
logging.basicConfig(level=logging.INFO)

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import api

if __name__ == "__main__":
    port = 5002
    host = '0.0.0.0'
    if os.environ.get('PORT') and os.environ.get('HOST'):
        port = int(os.environ.get('PORT'))
        docker_host = os.environ.get('HOST')
    logging.info('Starting worker on {}:{}'.format(host, port))
    app, _ = api.create_app(docker_host, port)
    app.run(debug=False, host=host, port=port)