from flask import Blueprint, jsonify, request

test_route = Blueprint("test_route", __name__)


@test_route.route("/", methods=["POST"])
def user_predict():
    data = request.get_json()
    return jsonify({data})
