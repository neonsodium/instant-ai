# from app import app
import json
import os
import zipfile
from io import BytesIO

from flask import Blueprint, abort, jsonify, request, send_file

demo_api_routes = Blueprint("demo_api_routes", __name__)

CLUSTER_FILES_DIR = "static/files_cluster"


@demo_api_routes.route("/download_cluster/<int:cluster_number>", methods=["GET"])
def get_cluster_files(cluster_number):
    file1 = f"Cluster_{str(cluster_number)}_Overview.pdf"
    file2 = f"cluster{str(cluster_number)}.csv"

    file1_path = os.path.join(CLUSTER_FILES_DIR, file1)
    file2_path = os.path.join(CLUSTER_FILES_DIR, file2)

    if not (os.path.exists(file1_path) and os.path.exists(file2_path)):
        abort(404, description="Files for the given cluster not found")

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.write(file1_path, os.path.basename(file1_path))
        zip_file.write(file2_path, os.path.basename(file2_path))

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"cluster_{cluster_number}_files.zip",
    )


@demo_api_routes.route("/download_cluster", methods=["POST"])
def post_cluster_files():
    data = request.get_json()
    if not data or "cluster_number" not in data or "level" not in data:
        abort(400, description="Invalid request: 'cluster_number' and 'level' are required")

    cluster_number = data["cluster_number"]
    level = data["level"]

    if level == 0:
        file1 = f"Cluster_{str(cluster_number)}_Overview.pdf"
        file2 = f"cluster{str(cluster_number)}.csv"

        file1_path = os.path.join(CLUSTER_FILES_DIR, file1)
        file2_path = os.path.join(CLUSTER_FILES_DIR, file2)
        print(file2_path, file1_path)

        if not (os.path.exists(file1_path) and os.path.exists(file2_path)):
            abort(404, description="Files for the given cluster and level not found")

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.write(file1_path, os.path.basename(file1_path))
            zip_file.write(file2_path, os.path.basename(file2_path))

    elif level == 1:
        zip_file_path = os.path.join(
            CLUSTER_FILES_DIR, f"hierarchical_cluster_for_{cluster_number}.zip"
        )
        print(zip_file_path)

        if not os.path.exists(zip_file_path):
            abort(404, description="ZIP file for the given cluster and level not found")

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.write(zip_file_path, os.path.basename(zip_file_path))
        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=os.path.basename(zip_file_path),
        )

    else:
        abort(400, description="Invalid level: supported levels are 0 and 1")

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"cluster_{cluster_number}_level_{level}_files.zip",
    )


def load_cluster_data():
    with open("static/json/cluster_data.json", "r") as file:
        return json.load(file)


def load_sub_cluster_data():
    with open("static/json/sub_cluster.json", "r") as file:
        return json.load(file)


@demo_api_routes.route("/sub_cluster/<cluster_number>", methods=["GET"])
def get_sub_cluster_data(cluster_number):
    clusters_data = load_sub_cluster_data()
    if cluster_number in clusters_data:
        return jsonify(clusters_data[cluster_number])
    else:
        return jsonify({"error": "Cluster not found"}), 404


@demo_api_routes.route("/sub_cluster", methods=["POST"])
def post_cluster_data():
    data = request.get_json()

    if "cluster_number" not in data:
        return jsonify({"error": "No cluster_number provided"}), 400

    cluster_number = str(data["cluster_number"])
    clusters_data = load_sub_cluster_data()
    if cluster_number in clusters_data:
        return jsonify(clusters_data[cluster_number])
    else:
        return jsonify({"error": "Cluster not found"}), 404


@demo_api_routes.route("/get_cluster_data", methods=["GET"])
def get_cluster_data():
    return load_cluster_data()
