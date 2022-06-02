from flask import Blueprint, jsonify, request, render_template
from voice_engine import voiceEngine
import secrets


voice = Blueprint('voice', __name__)
engine =  voiceEngine()


@voice.route('/voice/<condition>/<medium>', methods=['GET'])
def voice_condition(condition, medium):
    assignment_id = secrets.token_urlsafe(16)
    return render_template(f"{condition}_{medium}.html", 
                                demographics=True, 
                                condition=condition,
                                medium=medium,
                                assignmentID=assignment_id)


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

