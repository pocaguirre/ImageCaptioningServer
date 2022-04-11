from flask import Blueprint, jsonify, request, current_app, render_template, make_response
import string
import random
import numpy as np
import json
from inperson_engine import InPersonEngine
from multiprocessing import Value


inperson = Blueprint('inperson', __name__)
engine =  InPersonEngine(debug=True)
assignment_id = Value('i', 0)


@inperson.route('/inperson/<condition>', methods=['GET'])
def inperson_condition(condition):
    with assignment_id.get_lock():
        assignment_id.value += 1
        out = assignment_id.value
        return render_template(f"{condition}_extended.html", 
                                demographics=True, 
                                condition=condition, 
                                assignmentID=out)


@inperson.route('/inperson/submit', methods=['POST'])
def inperson_submit():
    answer = request.form['answer']
    condition = request.form['condition']
    demographics = request.form['demographics']
    assignment_id = request.form['assignmentID']
    worker_id = request.form['workerID']
    # extra = {k: v for k,v in request.form.items() if k not in ['answer', 'assignmentID', 'workerID', 'mturk', 'demographics']}
    success = engine.save_data(worker_id, assignment_id, condition, answer, demographics)
    return jsonify(success=success)
    # if success:
    #     if mturk_type not in current_app.config['MTURK_LINKS']:
    #         return jsonify({"link": "Error Link, wrong data provided: MTURK_TYPE"})
    #     else:
    #         if mturk_type == 'azure':
    #             if current_app.config['engine']._is_test_worker(worker_id):
    #                 return jsonify({"link": "/test"})
    #             if not current_app.config['engine']._check_valid_worker(worker_id):
    #                 return jsonify({"link": "done"})
    #             return jsonify({"link": f"/?worker={worker_id}"})
    #         else:
    #             return jsonify({"link": current_app.config['MTURK_LINKS'][mturk_type]})
    # return

@inperson.route('/inperson/get_images', methods=['POST'])
def inperson_get_images():
    worker_id = request.form['workerID']
    images = engine.get_images(worker_id)
    return jsonify(images)

@inperson.route('/inperson/dump/<table>', methods=['GET'])
def inperson_dump(table):
    result = engine.dump_table(table)
    return jsonify(result)

