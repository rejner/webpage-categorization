import os
# load .env file
from dotenv import load_dotenv
load_dotenv()
import logging
logging.basicConfig(level=logging.INFO)

import sys
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(__file__) + "/api")

import api.api_v1 as v1

if __name__ == "__main__":
    app, _ = v1.create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)