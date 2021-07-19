from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS, cross_origin

rating = Blueprint('rating', __name__)
# cors = CORS(api)


@rating.route('/rating', methods=['GET'])
def get_rating():
    data = request.args.get('data', default='Nothing Shared')
    return jsonify({"data": data})
