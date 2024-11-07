from flask import Blueprint, request, jsonify
user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/predict', methods=['POST'])
def user_predict():
    data = request.get_json()
    # prediction = predict(data)  # Assuming `predict` is a function you've defined
    return jsonify({"prediction": data})
