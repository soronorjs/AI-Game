from flask import Flask, request
from flask_cors import CORS
import json
import shelve

app = Flask(__name__)
CORS(app)


@app.route('/getresponse', methods=['POST'])
def get_response():
    infile = shelve.open("state")
    if 'data' in infile:
        data = infile["data"]
    else:
        data = {"Error": "Invalid Data"}
    print(json.dumps(data))
    return json.dumps(data), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)
