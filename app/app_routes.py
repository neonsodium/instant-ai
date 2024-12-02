import os

from flask import Blueprint, abort, jsonify, request, send_file

from app.filename_utils import *
from app.ml_models.summarising import summerise_cluster
from app.os_utils import *
from app.tasks import *

main_routes = Blueprint("main_routes", __name__)


@main_routes.route("/get_all_projects", methods=["GET", "POST"])
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


@main_routes.route("/create_new_project", methods=["GET", "POST"])
def create_new_project():
    new_project_id = create_project_uuid()
    result = create_directory(all_project_dir_path(), new_project_id)
    return jsonify({"project_id": new_project_id, **result})


@main_routes.route("/upload", methods=["POST"])
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


@main_routes.route("/check-task/<task_id>", methods=["GET"])
def check_task(task_id):
    result = celery.AsyncResult(task_id)
    return jsonify({"status": result.status})


@main_routes.route("/get_clusters", methods=["POST"])
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

    return jsonify(
        {"full_path": full_path, "project_id": project_id, "clusters": clusters}
    )


@main_routes.route("/process/feature_ranking", methods=["POST"])
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


@main_routes.route("/list-files", methods=["GET"])
def list_files():
    """
    Lists all files in the root directory and its subdirectories.
    """
    directory_project = all_project_dir_path()
    file_list = []
    for root, _, files in os.walk(directory_project):
        for file in files:
            full_path = os.path.join(root, file)
            # Make paths relative to the root directory
            relative_path = os.path.relpath(full_path, directory_project)
            file_list.append(relative_path)
    return jsonify({"files": file_list})


@main_routes.route("/download", methods=["GET"])
def download_file():
    """
    Downloads a file if the path is provided and valid.
    """
    directory_project = all_project_dir_path()
    relative_path = request.args.get("path", None)
    if not relative_path:
        return abort(400, description="The 'path' query parameter is required.")

    # Ensure the path is within the ROOT_DIRECTORY
    absolute_path = os.path.abspath(os.path.join(directory_project, relative_path))
    if not absolute_path.startswith(os.path.abspath(directory_project)):
        return abort(403, description="Access to the file is forbidden.")

    if not os.path.exists(absolute_path) or not os.path.isfile(absolute_path):
        return abort(404, description="File not found.")

    return send_file(absolute_path, as_attachment=True)


@main_routes.route("/process/summerising", methods=["POST"])
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


@main_routes.route("/process/time_series", methods=["POST"])
def start_time_series():
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
        summerise_cluster(data_raw, csv_file, json_file)

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


@main_routes.route("/process/cluster", methods=["POST"])
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
