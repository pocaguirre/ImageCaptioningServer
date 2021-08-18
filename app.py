from flask import Flask, jsonify, request, render_template, make_response
from model import Tasks, IMAGE_SETS
from api import api
from rating import rating, set_up
from helper import make_cookie, check_new_user, make_new_user, get_assignment
import logging
from flask_cors import CORS, cross_origin

app = Flask(__name__, static_folder='UserInterface/static', template_folder='UserInterface/static/tasks')
cors = CORS(app)
logging.basicConfig(level=logging.DEBUG)
app.config['engine'] = Tasks()
app.config['MTURK_LINKS'] = {
    "mturk": "https://worker.mturk.com/mturk/preview?groupId=",
    "sandbox": "https://workersandbox.mturk.com/mturk/preview?groupId=",
    "azure": "https://imagecaptioningicl.azurewebsites.net/"
}

app.register_blueprint(api)
app.register_blueprint(rating)
set_up()


@app.route('/', methods=['GET'])
def hello_world():
    user = check_new_user(request)
    if user is None:
        user = make_new_user()
    else:
        user = get_assignment(user, request)
    worker_id = user['worker_id']
    assignment_id = user['assignment_id']
    resp = make_response(render_template("main.html", mturk='azure',
                           workerID=f"{worker_id}",
                           assignID=f"{assignment_id}"))
    resp = make_cookie(worker_id, assignment_id, resp)
    return resp


@app.route('/test')
def test_interactions():
    return render_template("choose.html")


@app.route('/condition', methods=['GET'])
def get_condition():
    condition = request.args.get('condition', default=None)
    user = check_new_user(request)
    if user is None:
        user = make_new_user()
    else:
        user = get_assignment(user, request)
    worker_id = user['worker_id']
    assignment_id = user['assignment_id']
    _ = app.config['engine'].get_test_task(worker_id, assignment_id, condition)
    resp = make_response(render_template("main.html", mturk='azure',
                           workerID=worker_id,
                           assignID=assignment_id))
    return make_cookie(worker_id, assignment_id, resp)


@app.route("/interaction/<condition>")
@cross_origin()
def get_interaction_condition(condition):
    worker_id = request.cookies.get('workerID')
    demographics = not app.config['engine'].worker_has_demographics(worker_id)
    return render_template(f"{condition}_extended.html", demographics=demographics)


@app.route("/show_data")
def show_data():
    table = app.config['engine'].output_jobs()
    workers = app.config['engine'].get_workers()
    return render_template("data.html", table=table, workers=workers)


if __name__ == '__main__':
    app.run()
