from flask import Flask, jsonify, request
from model import Tasks

engine = Tasks()
app = Flask(__name__, static_folder='UserInterface/static')


@app.route('/')
def hello_world():
    return 'Hello, this is the server for the Image Captioning project. Go to https://github.com/pocaguirre/ImageCaptioningServer for more info.'


@app.route('/get_task', methods=['POST', 'GET'])
def get_task():
    if request.method == 'POST':
        worker_id = request.form['workerId']
        assignment_id = request.form['assignID']
        task = engine.get_task(worker_id, assignment_id)
        return jsonify(task)
    else:
        worker_id = "1"
        return jsonify(engine.get_test_task(worker_id))



@app.route('/reset_engine')
def reset_engine():
    global engine
    engine = Tasks()
    return "done"


if __name__ == '__main__':
    app.run()
