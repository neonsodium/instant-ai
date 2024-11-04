from app import app
from flask import jsonify,request
import os
import json
import uuid
from config import Config


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

def cluster_file_name_format(cluster_num) -> str:
    return f"cluster_{cluster_num}"

def full_path_of_cluster(level,path):
    # Create the list of formatted subdirectories
    sub_dirs = [cluster_file_name_format(cluster_num) for cluster_num in path]
    return join_os_path(project_dir_path(), *sub_dirs)

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
    level = request_data_json.get("level")
    path = request_data_json.get("path")
    
    # total paths should be equal to level
    if int(level) != len(path):
        return jsonify({"error": "Level and Path don't match"}), 400
    
    full_path = full_path_of_cluster(level, path)

    # Return the generated path as a JSON response
    return jsonify({"full_path": full_path})