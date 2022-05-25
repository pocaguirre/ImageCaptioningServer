from flask import Blueprint, jsonify, request, current_app, render_template, make_response
import string
import random
import numpy as np
import json
from voice_engine import voiceEngine
from multiprocessing import Value


voice = Blueprint('voice', __name__)
engine =  voiceEngine()
assignment_id = Value('i', 0)


@voice.route('/voice/<condition>/<medium>', methods=['GET'])
def voice_condition(condition, medium):
    with assignment_id.get_lock():
        assignment_id.value += 1
        out = assignment_id.value
        return render_template(f"{condition}_{medium}.html", 
                                demographics=True, 
                                condition=condition,
                                medium=medium,
                                assignmentID=out)


@voice.route('/voice/submit', methods=['POST'])
def voice_submit():
    data = {
        "answers_dict": request.form['answers'],
        "condition": request.form['condition'],
        "medium": request.form['medium'],
        "demographics": request.form['demographics'],
        "assignment_id": request.form['assignmentID'],
        "worker_id": request.form['workerID'],
        "calibrations": request.form['calibrations'],
        "answer_blobs": request.files
    }
    success = engine.save_data(data)
    return jsonify(success=success)


@voice.route('/voice/get_images', methods=['POST'])
def voice_get_images():
    worker_id = request.form['workerID']
    images = engine.get_images(worker_id)
    return jsonify(images)

