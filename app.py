from flask import Flask, jsonify, request
from model import Tasks
from applicationinsights.flask.ext import AppInsights

engine = Tasks()
app = Flask(__name__, static_folder='UserInterface/static')
app.config['APPINSIGHTS_INSTRUMENTATIONKEY'] = 'b2010324-c9a2-4838-9da9-d95fbaf83afd'
appinsights = AppInsights(app)


@app.after_request
def after_request(response):
    appinsights.flush()
    return response


@app.route('/')
def hello_world():
    return 'Hello, this is the server for the Image Captioning project. Go to https://github.com/pocaguirre/ImageCaptioningServer for more info.'


@app.route('/get_task', methods=['POST', 'GET'])
def get_task():
    # app.logger.debug("Getting new task")
    if request.method == 'POST':
        # app.logger.debug("Into POST request")
        worker_id = request.form['workerID']
        assignment_id = request.form['assignID']
        # app.logger.debug(f"WorkerID: {worker_id} AssignmentID: {assignment_id}")
        # task = engine.get_task(worker_id, assignment_id)
        # app.logger.debug(f"Task assigned: condition = {task['condition']} | image_set = {task['image_set']}")
        return jsonify({"task": "testing"})
    else:
        worker_id = "1"
        return jsonify(engine.get_test_task(worker_id))


@app.route('/reset_engine')
def reset_engine():
    global engine
    engine = Tasks()
    app.logger.info("RESETTING ENGINE")
    return "done"


if __name__ == '__main__':
    app.run()
