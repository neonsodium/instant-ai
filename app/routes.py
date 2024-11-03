from app import app
from flask import jsonify,abort,send_file,request
from werkzeug.utils import secure_filename
import os
import zipfile
from io import BytesIO
import json
import uuid
from config import Config


# ---------------------------------MAIN---API--------------------------------------- #

def create_uuid() -> str:
    return str(uuid.uuid4())

def join_os_path(base_dir, *sub_dirs):
    return os.path.join(base_dir, *sub_dirs)

def create_directory(base_dir, *sub_dirs) -> dict:
    """
    Creates a nested directory structure under the specified base directory.

    Usage:
        create_project_directory(app.config[Config.PROJECTS_DIR_VAR], 'dir1', 'dir11', 'task123')
        create_project_directory( project_dir_path(), 'dir1', 'dir11', 'task123')

    Args:
        base_dir (str): base directory under which subdirectories will be created.
        sub_dirs (str): Variable number of subdirectories to nest within the base directory.

    Returns:
        dict: A response indicating 'success' or 'error' with a message.
    """
    directory_path = join_os_path(base_dir, *sub_dirs)
    
    try:
        os.makedirs(directory_path, exist_ok=True)
        return {"status": "success", "message": f"Directory created at {directory_path}"}
    except OSError as e:
        return {"status": "error", "message": f"Failed to create directory: {e}"}
    

def load_processed_data(json_file_path) :
    with open(json_file_path, 'r') as json_file:
        return json.load(json_file)
    

def load_task_name(project_dir) -> str:
    project_name_path = os.path.join(project_dir, 'project_name.txt')
    if os.path.exists(project_name_path):
        with open(project_name_path, 'r') as f:
            return f.read().strip()  # Remove any surrounding whitespace
    return None
    
def project_dir_path() -> str:
    return app.config[Config.PROJECTS_DIR_VAR]

@app.route('/get_projects', methods=['GET','POST'])
def list_tasks():
    base_dir = project_dir_path()
    
    if not os.path.exists(base_dir):
        return jsonify({"error": "No tasks found"}), 404

    tasks = []
    
    try:
        for project_id in os.listdir(base_dir):
            task_dir = os.path.join(base_dir, project_id)
            if os.path.isdir(task_dir):
                # TODO project_name = load_project_name(project_dir)
                tasks.append({"project_id": project_id})
                # TODO tasks.append({"project_id": project_id, "project_name": project_name})

    except OSError as e:
        return jsonify({"error": f"An error occurred while accessing the directory: {str(e)}"}), 500

    return jsonify({"tasks": tasks}), 200


@app.route('/create_new_project',methods=['GET','POST'])
def create_new_project():
    '''TODO 
    if request.method == 'POST':
        #expect JSON input
        data = request.get_json()
        project_name = data.get('project_name')
    elif request.method == 'GET':
        project_name = request.args.get('project_name')
    if not project_name:
        return jsonify({"error": "project_name is required"}), 400
    ''' 
    
    new_project_id =  create_uuid()
    result = create_directory(project_dir_path(),new_project_id)
    return jsonify({"project_id": new_project_id, **result})

# TODO add a proper uri name
@app.route('/upload', methods=['POST'])
def upload_file():
    project_id = request.form.get('project_id', None)
    # TODO task_name = request.form.get('task_name', None)

    project_dir = os.path.join(project_dir_path(), project_id)

    # TODO
    # Create directory for the task ID if it doesn't exist
    # os.makedirs(project_dir, exist_ok=True)

    # TODO
    # if task_name:
    #     task_name_path = os.path.join(project_dir, 'task_name.txt')
    #     with open(task_name_path, 'w') as f:
    #         f.write(task_name)


    # Check if the 'file' part is present in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # TODO Check if the file uploaded is allowed i.e csv/xlsx
    if file:
        # filename = secure_filename(file.filename)
        filename = "data.csv"
        file_path = os.path.join(project_dir, filename)
        file.save(file_path)

        return jsonify({"message": f"File uploaded successfully!", "project_id": project_id}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400

@app.route('/get_clusters', methods=['POST'])
def display_cluster():
    '''
    curl -X POST http://localhost:8080/get_clusters \
    -H "Content-Type: application/json" \
    -d '{
            "level": 3,
            "path": [1, 2, 1]
        }'
    '''
    request_data_json = request.get_json()
    # Extract "level" and "path" from the JSON data
    level = request_data_json.get("level")
    path = request_data_json.get("path")
    
    if int(level) != len(path):
        return jsonify({"error": "Level and Path don't match"}), 400
    
    # Create the list of formatted subdirectories
    sub_dirs = [f"cluster_{element}" for element in path]
    
    full_path = join_os_path(project_dir_path(), *sub_dirs)

    # Return the generated path as a JSON response
    return jsonify({"full_path": full_path})



# ---------------------------------MAIN---API--------------------------------------- #























# ---------------------------------DEMO---API--------------------------------------- #
CLUSTER_FILES_DIR = "files_cluster"

@app.route('/download_cluster/<int:cluster_number>', methods=['GET'])
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

@app.route('/download_cluster', methods=['POST'])
def post_cluster_files():
    # Parse JSON data from the request
    data = request.get_json()
    if not data or 'cluster_number' not in data or 'level' not in data:
        abort(400, description="Invalid request: 'cluster_number' and 'level' are required")

    cluster_number = data['cluster_number']
    level = data['level']

    if level == 0:
        # Level 0 filenames
        file1 = f"Cluster_{str(cluster_number)}_Overview.pdf"
        file2 = f"cluster{str(cluster_number)}.csv"
        
        # Construct full file paths
        file1_path = os.path.join(CLUSTER_FILES_DIR, file1)
        file2_path = os.path.join(CLUSTER_FILES_DIR, file2)
        print(file2_path,file1_path)
        # Check if both files exist for level 0
        if not (os.path.exists(file1_path) and os.path.exists(file2_path)):
            abort(404, description="Files for the given cluster and level not found")

        # Create a ZIP file in memory containing the requested files for level 0
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.write(file1_path, os.path.basename(file1_path))
            zip_file.write(file2_path, os.path.basename(file2_path))

    elif level == 1:
        # For level 1, look for the pre-existing ZIP file
        zip_file_path = os.path.join(CLUSTER_FILES_DIR,f"hierarchical_cluster_for_{cluster_number}.zip")
        print(zip_file_path)
        
        if not os.path.exists(zip_file_path):
            abort(404, description="ZIP file for the given cluster and level not found")
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.write(zip_file_path, os.path.basename(zip_file_path))
        zip_buffer.seek(0)
        
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=os.path.basename(zip_file_path)
        )

    else:
        abort(400, description="Invalid level: supported levels are 0 and 1")

    # Set the buffer's position to the beginning of the stream
    zip_buffer.seek(0)

    # Send the ZIP file as a response
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'cluster_{cluster_number}_level_{level}_files.zip'
    )

def load_cluster_data():
    with open('json/cluster_data.json', 'r') as file:
        return json.load(file)

def load_sub_cluster_data():
    with open('json/sub_cluster.json', 'r') as file:
        return json.load(file)

@app.route('/sub_cluster/<cluster_number>', methods=['GET'])
def get_sub_cluster_data(cluster_number):
    # Check if the cluster number exists in the dictionary
    clusters_data = load_sub_cluster_data()
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


# ---------------------------------DEMO---API--------------------------------------- #