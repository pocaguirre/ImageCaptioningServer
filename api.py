from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS, cross_origin
from model import Tasks, IMAGE_SETS

api = Blueprint('api', __name__)
cors = CORS(api)
# TODO: Fix mturk and sandbox links on javascript main


@api.route('/get_task', methods=['POST', 'GET'])
@cross_origin()
def get_task():
    if request.method == 'POST':
        worker_id = request.form['workerID']
        assignment_id = request.form['assignID']
        if not current_app.config['engine']._check_worker_exists(worker_id):
            current_app.logger.info(f'NEW WORKER: {worker_id}')
        if current_app.config['engine']._is_new_assignment(assignment_id):
            current_app.logger.info(f"NEW ASSIGNMENT: {assignment_id}")
        task = current_app.config['engine'].get_task(worker_id, assignment_id)
        task['worker'] = worker_id
        task['assignment'] = assignment_id
        return jsonify(task)


@api.route('/submit_data', methods=['POST'])
@cross_origin()
def submit_data():
    answer = request.form['answer']
    assignment_id = request.form['assignmentID']
    worker_id = request.form['workerID']
    mturk_type = request.form['mturk']
    worker_object = request.form['demographics']
    success = current_app.config['engine'].save_anwer(assignment_id, answer, worker_id, worker_object)
    if success:
        if mturk_type not in current_app.config['MTURK_LINKS']:
            return jsonify({"link": "Error Link, wrong data provided: MTURK_TYPE"})
        else:
            if mturk_type == 'azure':

                if current_app.config['engine']._is_test_worker(worker_id):
                    return jsonify({"link": "/test"})
                if not current_app.config['engine']._check_valid_worker(worker_id):
                    return jsonify({"link": "done"})
                return jsonify({"link": f"/?worker={worker_id}"})
            else:
                return jsonify({"link": current_app.config['MTURK_LINKS'][mturk_type]})


@api.route('/reset_engine')
def reset_engine():
    current_app.config['engine'] = Tasks()
    current_app.logger.info("RESETTING ENGINE")
    return "done"


@api.route("/export_raw_data")
def export_raw():
    return jsonify(current_app.config['engine'].export_raw_data())


