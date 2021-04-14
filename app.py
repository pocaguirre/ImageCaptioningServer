from flask import Flask, jsonify, request, render_template
from model import Tasks
from applicationinsights.flask.ext import AppInsights
from flask_cors import CORS, cross_origin

engine = Tasks()
app = Flask(__name__, static_folder='UserInterface/static', template_folder='UserInterface/static/tasks')
app.config['APPINSIGHTS_INSTRUMENTATIONKEY'] = 'b2010324-c9a2-4838-9da9-d95fbaf83afd'
appinsights = AppInsights(app)
cors = CORS(app)
local_worker = 0
local_assignment = 0


@app.after_request
def after_request(response):
    appinsights.flush()
    return response


@app.route('/', methods=['GET'])
def hello_world():
    worker_id = request.args.get('worker', default=None)
    assignment_id = request.args.get('assignment', default=None)
    if worker_id is None:
        global local_worker
        local_worker += 1
        worker_id = local_worker
    if assignment_id is None:
        global local_assignment
        local_assignment += 1
        assignment_id = local_assignment
    return render_template("main.html", mturk=False,
                           workerID=f"worker{worker_id}",
                           assignID=f"assignment{assignment_id}")


@app.route('/condition/<condition>', methods=['GET'])
@cross_origin()
def get_condition(condition):
    mturk = request.args.get('mturk', default=None)
    return render_template(f"{condition}.html", mturk=mturk)


@app.route('/submit_data', methods=['POST'])
@cross_origin()
def submit_data():
    answer = request.form['answer']
    assignment_id = request.form['assignmentID']
    worker_id = request.form['workerID']
    success = engine.save_anwer(assignment_id, answer)
    if success:
        return jsonify({"link": f"https://imagecaptioningicl.azurewebsites.net/?worker={worker_id}"})


@app.route('/get_task', methods=['POST', 'GET'])
@cross_origin()
def get_task():
    # app.logger.debug("Getting new task")
    if request.method == 'POST':
        # app.logger.debug("Into POST request")
        worker_id = request.form['workerID']
        assignment_id = request.form['assignID']
        # app.logger.debug(f"WorkerID: {worker_id} AssignmentID: {assignment_id}")
        task = engine.get_task(worker_id, assignment_id)
        # app.logger.debug(f"Task assigned: condition = {task['condition']} | image_set = {task['image_set']}")
        return jsonify(task)
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
