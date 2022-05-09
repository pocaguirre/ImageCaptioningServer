from flask import Blueprint, jsonify, request, current_app, render_template, make_response
import string
import random
import numpy as np
import json
from inperson_engine import InPersonEngine
from multiprocessing import Value


inperson = Blueprint('inperson', __name__)
engine =  InPersonEngine()
assignment_id = Value('i', 0)


@inperson.route('/inperson/setup', methods=['POST'])
def inperson_setup():
    engine.setup_connection()
    return jsonify("successs")


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
    calibrations = request.form['calibrations']
    success = engine.save_data(worker_id, assignment_id, condition, answer, demographics, calibrations)
    return jsonify(success=success)


@inperson.route('/inperson/get_images', methods=['POST'])
def inperson_get_images():
    worker_id = request.form['workerID']
    images = engine.get_images(worker_id)
    return jsonify(images)

