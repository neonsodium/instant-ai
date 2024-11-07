import os
import json
import uuid
from . import app
from config import Config
from .tasks import example_task
from flask import jsonify,request,Blueprint
from .ml_models.label_encode_data import label_encode_data
from .ml_models.optimised_feature_rank import feature_ranking_algorithm

# TODO add main route
# split main route
# main_routes = Blueprint('main_routes', __name__)

def create_uuid() -> str:
    return str(uuid.uuid4())

def secure_join_os_path(base_dir: str, *sub_dirs: str) -> str:
    full_path = os.path.abspath(
        os.path.join(base_dir, *sub_dirs)
    )
    if not full_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Unsafe path detected.")
    
    return full_path

def create_directory(base_dir: str, *sub_dirs: str) -> dict:
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
    directory_path = secure_join_os_path(base_dir, *sub_dirs)
    
    try:
        os.makedirs(directory_path, exist_ok=True)
        return {"status": "success", "message": f"Directory created at {directory_path}"}
    except OSError as e:
        return {"status": "error", "message": f"Failed to create directory: {e}"}
    

def load_processed_data(json_file_path: str) :
    with open(json_file_path, 'r') as json_file:
        return json.load(json_file)
    

def load_project_name(project_dir: str) -> str:
    project_name_path = os.path.join(project_dir, 'project_name.txt')
    if os.path.exists(project_name_path):
        with open(project_name_path, 'r') as f:
            return f.read().strip()  # Remove any surrounding whitespace
    return None
    
def all_project_dir_path() -> str:
    return app.config[Config.PROJECTS_DIR_VAR]

def list_sub_directories(base_dir: str) -> list:
    list_sub_dir = []
    
    for project_id in os.listdir(base_dir):
        project_dir = os.path.join(base_dir, project_id)
        if os.path.isdir(project_dir):
            # TODO project_name = load_project_name(project_dir)
            list_sub_dir.append(project_id)
            # TODO tasks.append({"project_id": project_id, "project_name": project_name})
    
    return list_sub_dir

@app.route('/get_all_projects', methods=['GET','POST'])
def list_tasks():
    
    if not os.path.exists(all_project_dir_path()):
        return jsonify({"error": "Project directory not configured"}), 404
    
    try:
        tasks: list = list_sub_directories(all_project_dir_path())

    except OSError as e:
        return jsonify({"error": f"An error occurred while accessing the directory: {str(e)}"}), 500

    return jsonify({"tasks": tasks}), 200

@app.route('/start_task', methods=['POST'])
def start_task():
    data = request.json.get('data')
    
    # Trigger the Celery task
    task = example_task.apply_async(args=[data])
    
    # Return task ID to client
    return jsonify({"message": "Task started", "task_id": task.id})


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
    result = create_directory(
        all_project_dir_path(),
        new_project_id
    )
    return jsonify({"project_id": new_project_id, **result})

# TODO add a proper uri name
@app.route('/upload', methods=['POST'])
def upload_file():
    project_id = os.path.basename(request.form.get('project_id'))
    # TODO project_name = request.form.get('project_name')
    project_dir = os.path.join(
        all_project_dir_path(), 
        project_id
    )

    if not os.path.isdir(project_dir):
        return jsonify({"error": "Invaild Project Id"}), 400
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    # TODO
    # Create directory for the task ID if it doesn't exist
    # os.makedirs(project_dir, exist_ok=True)

    # TODO
    # if task_name:
    #     task_name_path = os.path.join(project_dir, 'task_name.txt')
    #     with open(task_name_path, 'w') as f:
    #         f.write(task_name)


    # Check if the 'file' part is present in the request

    file = request.files['file']

    # TODO Check if the file uploaded is allowed i.e csv/xlsx
    if file:
        # filename = secure_filename(file.filename)
        raw_data_filename = "data_raw.csv"
        label_encode_filename = "label_encode_data.csv"
        raw_data_file_path = os.path.join(project_dir, raw_data_filename)
        label_encode_file_path = os.path.join(project_dir, label_encode_filename)
        file.save(raw_data_file_path)
        label_encode_data(
            raw_data_file_path,
            label_encode_file_path
        )

        return jsonify({"message": f"File uploaded successfully!", "project_id": project_id}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400

def cluster_file_name_format(cluster_num: str | int) -> str:
    return f"cluster_{cluster_num}"

def full_path_of_dir(project_id: str,path: list):
    # Create the list of formatted subdirectories
    sub_dirs = [cluster_file_name_format(cluster_num) for cluster_num in path]
    return secure_join_os_path(
        secure_join_os_path(
            all_project_dir_path(),
            project_id
        ),
        *sub_dirs
    )

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
    level = int(request_data_json.get("level"))
    path = request_data_json.get("path")
    project_id = os.path.basename(request_data_json.get("project_id"))
    del request_data_json
    # total paths should be equal to level
    if int(level) != len(path):
        return jsonify({"error": "Level and Path don't match"}), 400
    
    full_path = full_path_of_dir(project_id,path)
    clusters = list_sub_directories(full_path)

    # Return the generated path as a JSON response
    return jsonify({"full_path": full_path,"project_id": project_id,"clusters": clusters})


@app.route('/process',methods=['POST'])
def start_sub_clustering():
    '''
    curl -X POST http://127.0.0.1:5000/process -H "Content-Type: application/json" -d '{
    "target_vars": ["reading_fee_paid", "Number_of_Months", "Coupon_Discount", "num_books", "magazine_fee_paid", "Renewal_Amount", "amount_paid"],
    "target_var": "amount_paid"
    }'
    '''
    request_data_json = request.get_json()
    project_id = os.path.basename(request_data_json.get("project_id"))
    path = request_data_json.get("path")
    target_vars = request_data_json.get('target_vars', [])
    target_var = request_data_json.get('target_var', None)
    

    # target_vars = ['reading_fee_paid', 'Number_of_Months', 'Coupon_Discount','num_books', 'magazine_fee_paid', 'Renewal_Amount','amount_paid']
    # target_var = "amount_paid"
    feature_ranking_algorithm(target_var,target_vars,full_path_of_dir(project_id,path))

    return jsonify({"Status": "Process started"})