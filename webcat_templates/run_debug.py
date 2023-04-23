import os
import logging
logging.basicConfig(level=logging.INFO)

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import api

if __name__ == "__main__":
    app, _ = api.create_app()
    app.run(debug=True, host='0.0.0.0', port=5002, use_debugger=False, use_reloader=False)