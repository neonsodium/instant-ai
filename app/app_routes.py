import os

from flask import jsonify, request

from app.filename_utils import *
from app.os_utils import *
from app.tasks import *
from app.ml_models.summarising import summerise_cluster

from . import app  # TODO Change it to current app -> from flask import current_app

# TODO add main route
# split main route
# main_routes = Blueprint('main_routes', __name__)


@app.route("/get_all_projects", methods=["GET", "POST"])
def list_tasks():

    if not os.path.exists(all_project_dir_path()):
        return jsonify({"error": "Project directory not configured"}), 404

    try:
        projects: list = list_sub_directories(all_project_dir_path())

    except OSError as e:
        return (
            jsonify(
                {"error": f"An error occurred while accessing the directory: {str(e)}"}
            ),
            500,
        )

    return jsonify({"projects": projects}), 200


@app.route("/create_new_project", methods=["GET", "POST"])
def create_new_project():
    new_project_id = create_project_uuid()
    result = create_directory(all_project_dir_path(), new_project_id)
    return jsonify({"project_id": new_project_id, **result})


@app.route("/upload", methods=["POST"])
def upload_file():
    project_id = os.path.basename(request.form.get("project_id"))
    project_dir = directory_project_path_full(project_id, [])

    if not os.path.isdir(project_dir):
        return jsonify({"error": "Invalid Project ID"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file:
        result = async_save_and_process_file.delay(project_dir, file.read())

        return (
            jsonify({"message": "File processing has started", "task_id": result.id}),
            202,
        )
    else:
        return jsonify({"error": "Invalid file type"}), 400


@app.route("/check-task/<task_id>", methods=["GET"])
def check_task(task_id):
    result = celery.AsyncResult(task_id)
    return jsonify({"status": result.status})


@app.route("/get_clusters", methods=["POST"])
def display_cluster():
    """
    curl -X POST http://localhost:8080/get_clusters \
    -H "Content-Type: application/json" \
    -d '{
            "level": 3,
            "path": [1, 2, 1]
        }'
    """

    request_data_json = request.get_json()
    level = int(request_data_json.get("level"))
    path = request_data_json.get("path")
    project_id = os.path.basename(request_data_json.get("project_id"))
    del request_data_json
    # total paths should be equal to level
    if int(level) != len(path):
        return jsonify({"error": "Level and Path don't match"}), 400

    full_path = directory_project_path_full(project_id, path)
    clusters = list_sub_directories(full_path)

    # Return the generated path as a JSON response
    return jsonify(
        {"full_path": full_path, "project_id": project_id, "clusters": clusters}
    )


@app.route("/process/feature_ranking", methods=["POST"])
def start_feature_ranking():
    """
    curl -X POST http://127.0.0.1:8080/process/feature_ranking -H "Content-Type: application/json" -d '{
    "target_vars_list": ["reading_fee_paid", "Number_of_Months", "Coupon_Discount", "num_books", "magazine_fee_paid", "Renewal_Amount", "amount_paid"],
    "target_var": "amount_paid",
    "level": 3,
    "path": [1, 2, 1]
    }'
    """
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))
    list_path = request_data_json.get("path")
    target_vars_list = request_data_json.get("target_vars_list", [])
    target_var = request_data_json.get("target_var", None)

    target_vars_list = [
        "reading_fee_paid",
        "Number_of_Months",
        "Coupon_Discount",
        "num_books",
        "magazine_fee_paid",
        "Renewal_Amount",
        "amount_paid",
    ]
    target_var = "amount_paid"
    directory_project = directory_project_path_full(project_id, list_path)
    result = async_optimised_feature_rank.delay(
        target_var, target_vars_list, directory_project
    )
    return (
        jsonify(
            {
                "message": "File encoding has started",
                "task_id": str(result.id),
                "Project_id": project_id,
                "project_dir": os.path.join(
                    directory_project, filename_label_encoded_data_csv()
                ),
            }
        ),
        202,
    )


@app.route("/process/summerising", methods=["POST"])
def start_summerising():
    """
    curl -X POST http://127.0.0.1:8080/process/summerising -H "Content-Type: application/json" -d '{
    "level": 3,
    "path": [1, 2, 1]
    }'
    """
    request_data_json = request.get_json()
    level = int(request_data_json.get("level"))
    path = request_data_json.get("path")
    project_id = os.path.basename(request_data_json.get("project_id"))
    del request_data_json
    # total paths should be equal to level
    if int(level) != len(path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_project = directory_project_path_full(project_id, path)
    clusters = list_sub_directories(directory_project)

    for cluster in clusters:
        data_raw = os.path.join(directory_project, cluster, filename_raw_data_csv())
        json_file = os.path.join(
            directory_project, cluster, feature_descriptions_json()
        )
        csv_file = os.path.join(directory_project, cluster, feature_descriptions_csv())
        summerise_cluster(data_raw, json_file, csv_file)

    return (
        jsonify(
            {
                "message": "File encoding has started",
                "Project_id": project_id,
                "project_dir": os.path.join(
                    directory_project, filename_label_encoded_data_csv()
                ),
            }
        ),
        202,
    )


@app.route("/process/cluster", methods=["POST"])
def start_sub_clustering():
    """
    curl -X POST http://127.0.0.1:8080/process -H "Content-Type: application/json" -d '{
    "target_var": "amount_paid",
    "level": 3,
    "path": [1, 2, 1]
    }'
    """
    # TODO add target varibale
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))
    list_path = request_data_json.get("path")
    level = int(request_data_json.get("level"))
    path = request_data_json.get("path")
    if int(level) != len(path):
        return jsonify({"error": "Level and Path don't match"}), 400

    directory_project_base = directory_project_path_full(project_id, [])
    directory_project_cluster = directory_project_path_full(project_id, list_path)
    input_file_path_feature_rank_pkl = os.path.join(
        directory_project_base, filename_feature_rank_list_pkl()
    )

    if not os.path.exists(input_file_path_feature_rank_pkl):
        return (
            jsonify(
                {"error": "Feature ranking file not found", "project_id": project_id}
            ),
            404,
        )

    result = async_optimised_clustering.delay(
        directory_project_cluster, input_file_path_feature_rank_pkl
    )

    return (
        jsonify(
            {
                "message": "Clustering has started",
                "task_id": result.id,
                "Project_id": project_id,
                "project_dir": directory_project_cluster,
            }
        ),
        202,
    )
