from os import path
import sys
sys.path.append(path.dirname(__file__))

import api.api_v1 as v1

if __name__ == "__main__":
    v1.app.run(debug=True)