from os import path
import sys
sys.path.append(path.dirname(__file__))
sys.path.append(path.dirname(__file__) + "/api")

import api.api_v1 as v1

if __name__ == "__main__":
    app, _ = v1.create_app('config.py')
    app.run(debug=False, host='0.0.0.0', port=5000)