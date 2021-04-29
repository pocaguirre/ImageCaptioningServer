from flask import Flask, jsonify, request, render_template
from model import Tasks, IMAGE_SETS
from applicationinsights.flask.ext import AppInsights
from flask_cors import CORS, cross_origin

engine = Tasks()
app = Flask(__name__, static_folder='UserInterface/static', template_folder='UserInterface/static/tasks')
app.config['APPINSIGHTS_INSTRUMENTATIONKEY'] = 'b2010324-c9a2-4838-9da9-d95fbaf83afd'
appinsights = AppInsights(app)
cors = CORS(app)
local_worker = 0
local_assignment = 0
MTURK_LINKS = {
    "mturk": "https://worker.mturk.com/mturk/preview?groupId=",
    "sandbox": "https://workersandbox.mturk.com/mturk/preview?groupId=",
    "azure": "https://imagecaptioningicl.azurewebsites.net/"
}


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
    return render_template("main.html", mturk='azure',
                           workerID=f"worker{worker_id}",
                           assignID=f"assignment{assignment_id}")


@app.route('/condition', methods=['GET'])
def get_condition():
    global engine
    condition = request.args.get('condition', default=None)
    global local_worker
    local_worker += 1
    worker_id = local_worker
    global local_assignment
    local_assignment += 1
    assignment_id = local_assignment
    task = engine.get_test_task(f"worker{worker_id}", f"assignment{assignment_id}", condition)
    return render_template("main.html", mturk='azure',
                           workerID=f"worker{worker_id}",
                           assignID=f"assignment{assignment_id}",
                           condition1=condition,
                           condition2=task['html'].split()[0].split("/")[-1].split(".")[0])


@app.route('/test')
def test_interactions():
    return render_template("choose.html")


@app.route('/submit_data', methods=['POST'])
@cross_origin()
def submit_data():
    global engine
    answer = request.form['answer']
    assignment_id = request.form['assignmentID']
    worker_id = request.form['workerID']
    mturk_type = request.form['mturk']
    success = engine.save_anwer(assignment_id, answer)
    if success:
        if mturk_type not in MTURK_LINKS:
            return jsonify({"link": "Error Link, wrong data provided: MTURK_TYPE"})
        else:
            if mturk_type == 'azure':
                if engine._is_test_worker(worker_id):
                    return jsonify({"link": "/test"})
                return jsonify({"link": f"/?worker={worker_id}"})
            else:
                return jsonify({"link": MTURK_LINKS[mturk_type]})


@app.route('/get_task', methods=['POST', 'GET'])
@cross_origin()
def get_task():
    global engine
    # app.logger.debug("Getting new task")
    if request.method == 'POST':
        # app.logger.debug("Into POST request")
        worker_id = request.form['workerID']
        assignment_id = request.form['assignID']
        # app.logger.debug(f"WorkerID: {worker_id} AssignmentID: {assignment_id}")
        task = engine.get_task(worker_id, assignment_id)
        # app.logger.debug(f"Task assigned: condition = {task['condition']} | image_set = {task['image_set']}")
        return jsonify(task)


@app.route('/reset_engine')
def reset_engine():
    global engine
    engine = Tasks()
    app.logger.info("RESETTING ENGINE")
    return "done"


@app.route("/show_data")
def show_data():
    global engine
    table = engine.output_jobs()
    workers = engine.get_workers()
    return render_template("data.html", table=table, workers=workers)


@app.route("/interaction/<condition>")
def get_interaction_condition(condition):
    return render_template(f"{condition}_extended.html")


if __name__ == '__main__':
    app.run()
