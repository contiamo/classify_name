import logging
import os

import handler
from flask import Flask, request

print('Index starting')

bundle_root = os.environ.get('LABS_BUNDLE_ROOT', '/labs/project')


app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


print('Server starting')


@app.route("/", methods=["POST", "GET"])
def main_route():
    logger.debug("running main_route")
    try:
        print('Calling handler')
        data = request.get_data()
        print(data, type(data), request.data, request.get_json(), request.form, str(data))
        ret = handler.handle(str(data))
        return ret
    except Exception as e:
        # get all error arguments as strings
        whole_error = ''
        for arg in e.args:
            whole_error += ' ' + arg
        return whole_error


if __name__ == '__main__':
    logger.debug("starting function server at 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
