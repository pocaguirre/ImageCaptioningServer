from flask import Blueprint, jsonify, request, current_app, render_template
from flask_cors import CORS, cross_origin

rating = Blueprint('rating', __name__)
# cors = CORS(api)


@rating.route('/rating', methods=['GET'])
def get_rating():
    return render_template("rating.html")
