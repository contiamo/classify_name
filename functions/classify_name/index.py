import logging
import os

import handler
from flask import Flask, request

print('Index starting')

bundle_root = os.environ.get('LABS_BUNDLE_ROOT', '/labs/project')


app = Flask(__name__)



print('Server starting')


@app.route("/", methods=["POST", "GET"])
def main_route():
    print('Calling handler')
    data = request.get_data()
    print(data, type(data), request.data, request.get_json(), request.form, str(data))
    ret = handler.handle(data)
    print('Output from function is {}'.format(ret))
    return ret



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
