from flask import Flask, jsonify, request, abort
import json
import zipfile
from io import BytesIO
import os

app = Flask(__name__)

# Load the JSON data from the file
def load_cluster_data():
    with open('cluster_data.json', 'r') as file:
        return json.load(file)

def load_sub_cluster_data():
    with open('sub_cluster.json', 'r') as file:
        return json.load(file)

@app.route('/sub_cluster/<cluster_number>', methods=['GET'])
def get_sub_cluster_data(cluster_number):
    # Check if the cluster number exists in the dictionary
    clusters_data = load_sub_cluster_data()
    print(type(cluster_number))
    if cluster_number in clusters_data:
        return jsonify(clusters_data[cluster_number])
    else:
        return jsonify({"error": "Cluster not found"}), 404

# Endpoint for POST request
@app.route('/sub_cluster', methods=['POST'])
def post_cluster_data():
    # Get the JSON data from the POST request
    data = request.get_json()

    # Validate if the 'cluster_number' is provided

    if 'cluster_number' not in data:
        return jsonify({"error": "No cluster_number provided"}), 400

    cluster_number = str(data['cluster_number'])
    clusters_data = load_sub_cluster_data()
    # Check if the cluster number exists in the dictionary
    if cluster_number in clusters_data:
        return jsonify(clusters_data[cluster_number])
    else:
        return jsonify({"error": "Cluster not found"}), 404

@app.route('/get_cluster_data', methods=['GET'])
def get_cluster_data():
    return load_cluster_data()

from flask import Flask, send_file, jsonify, abort
import os

app = Flask(__name__)

# Directory where the cluster files are stored
CLUSTER_FILES_DIR = "files_cluster"

@app.route('/something/<int:cluster_number>', methods=['GET'])
def get_cluster_files(cluster_number):
    # Generate the filenames based on the cluster number
    file1 = f"Cluster_{str(cluster_number)}_Overview.pdf"
    file2 = f"cluster{str(cluster_number)}.csv"
    
    # Construct full file paths
    file1_path = os.path.join(CLUSTER_FILES_DIR, file1)
    file2_path = os.path.join(CLUSTER_FILES_DIR, file2)
    
    # Check if both files exist
    if not (os.path.exists(file1_path) and os.path.exists(file2_path)):
        abort(404, description="Files for the given cluster not found")
    
    # If both files exist, return them as a response
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.write(file1_path, os.path.basename(file1_path))
        zip_file.write(file2_path, os.path.basename(file2_path))
    
    # Set the buffer's position to the beginning of the stream
    zip_buffer.seek(0)
    
    # Send the ZIP file
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name=f'cluster_{cluster_number}_files.zip')

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
