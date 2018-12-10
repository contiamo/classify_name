from flask import Flask, request
import handler

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def main_route():
    data = request.get_data().decode('ascii')
    ret = handler.handle(data)
    return ret

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
