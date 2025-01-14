# @processor_routes.route("/<project_id>/time-series/analysis", methods=["POST", "GET"])
# def initiate_time_series(project_id):
#     task_name = "time_series_analysis"
#     request_data_json = request.get_json()
#     project_id = os.path.basename(request_data_json.get("project_id"))
#     user_added_vars_list = request_data_json.get("user_added_vars_list", [])
#     list_path = request_data_json.get("path")
#     kpi = request_data_json.get("kpi", None)
#     no_of_months = request_data_json.get("no_of_months")
#     date_column = request_data_json.get("date_column")
#     increase_factor = request_data_json.get("increase_factor")
#     zero_value_replacement = request_data_json.get("zero_value_replacement")

#     project = project_model.collection.find_one({"_id": project_id})

#     if not project:
#         return jsonify({"error": "Invalid Project ID"}), 400

#     directory_project = directory_project_path_full(project_id, [])
#     if not os.path.isdir(directory_project):
#         return jsonify({"error": "Invalid Project ID"}), 400

#     directory_project_cluster = directory_project_path_full(project_id, list_path)
#     if not os.path.exists(directory_project_cluster):
#         return jsonify({"error": "Cluster Does not exist.", "project_id": project_id}), 404

#     if not os.path.isfile(os.path.join(directory_project_cluster, filename_raw_data_csv())):
#         return jsonify({"message": "Data set not found"}), 400

#     raw_data_file = os.path.join(directory_project_cluster, filename_raw_data_csv())

#     task_params = {
#         "project_id": project_id,
#         "kpi": kpi,
#         "task_name": task_name,
#         "increase_factor": increase_factor,
#         "zero_value_replacement": zero_value_replacement,
#         "no_of_months": no_of_months,
#         "path": list_path,
#         "user_added_vars_list": user_added_vars_list,
#     }
#     task_key = generate_task_key(**task_params)

#     existing_task_id = redis_client.get(task_key)
#     if existing_task_id:
#         return (
#             jsonify(
#                 {
#                     "message": "Task is already running",
#                     "task_id": existing_task_id.decode(),
#                     "project_id": project_id,
#                 }
#             ),
#             200,
#         )

#     result = async_time_series_analysis.apply_async(
#         args=[
#             directory_project_cluster,
#             raw_data_file,
#             user_added_vars_list,
#             kpi,
#             no_of_months,
#             date_column,
#             increase_factor,
#             zero_value_replacement,
#         ],
#         kwargs={"project_id": project_id, "task_key": task_key},
#     )

#     task_info = {
#         "task_id": result.id,
#         "project_id": project_id,
#         "status": "pending",
#         "kpi": kpi,
#         "start_time": datetime.now().isoformat(),
#         "params": task_params,
#         "task_name": task_name,
#     }

#     redis_client.hset("running_tasks", result.id, json.dumps(task_info))

#     project_model.add_task_metadata(project_id, result.id, task_info)

#     redis_client.setex(
#         task_key, current_app.config.get("REDIS_TIMEOUT_TASK_ID"), f"task:{result.id}"
#     )  # Key expires time

#     return (
#         jsonify(
#             {
#                 "message": "Time series analysis has started",
#                 "task_id": str(result.id),
#                 "project_id": project_id,
#             }
#         ),
#         202,
#     )

# @processor_routes.route("/<project_id>/clusters/subcluster", methods=["POST"])
# def initiate_subclustering(project_id):
#     task_name = "clustering"
#     request_data_json = request.get_json()
#     list_path = request_data_json.get("path")
#     kpi = request_data_json.get("kpi")

#     project = project_model.collection.find_one({"_id": project_id})

#     if not project:
#         return jsonify({"error": "Invalid Project ID"}), 400

#     directory_project_base = directory_project_path_full(project_id, [])
#     if not os.path.isdir(directory_project_base):
#         return jsonify({"error": "Invalid Project ID"}), 400

#     if not os.path.isfile(os.path.join(directory_project_base, filename_raw_data_csv())):
#         return jsonify({"message": "Data set not uploaded"}), 400

#     if not kpi:
#         return jsonify({"error": "Missing 'kpi' in request"}), 400

#     input_file_path_feature_rank_pkl = os.path.join(
#         directory_project_base, filename_feature_rank_list_pkl(kpi)
#     )
#     if not os.path.exists(input_file_path_feature_rank_pkl):
#         return (
#             jsonify(
#                 {"error": f"Feature ranking file for {kpi} not found.", "project_id": project_id}
#             ),
#             404,
#         )

#     directory_project_cluster = directory_project_path_full(project_id, list_path)
#     if not os.path.exists(directory_project_cluster):
#         return (jsonify({"error": "Cluster does not exist.", "project_id": project_id}), 404)

#     task_params = {
#         "project_id": project_id,
#         "kpi": kpi,
#         "list_path": list_path,
#         "task_name": task_name,
#     }
#     task_key = generate_task_key(**task_params)

#     existing_task_id = redis_client.get(task_key)
#     if existing_task_id:
#         return (
#             jsonify(
#                 {
#                     "message": "Task is already running",
#                     "task_id": existing_task_id.decode(),
#                     "project_id": project_id,
#                 }
#             ),
#             200,
#         )

#     result = async_optimised_clustering.apply_async(
#         args=[directory_project_cluster, input_file_path_feature_rank_pkl],
#         kwargs={"project_id": project_id, "task_key": task_key},
#     )

#     task_info = {
#         "task_id": result.id,
#         "status": "pending",
#         "project_id": project_id,
#         "kpi": kpi,
#         "start_time": datetime.now().isoformat(),
#         "params": task_params,
#     }

#     redis_client.hset("running_clustering_tasks", result.id, json.dumps(task_info))

#     project_model.add_task_metadata(project_id, result.id, task_info)

#     # Set Redis key expiration time for task management
#     redis_client.setex(
#         task_key, current_app.config.get("REDIS_TIMEOUT_TASK_ID"), f"task:{result.id}"
#     )  # Key expires time

#     return (
#         jsonify(
#             {"message": "Clustering has started", "task_id": result.id, "project_id": project_id}
#         ),
#         202,
#     )


# @processor_routes.route("/<project_id>/features/ranking", methods=["POST"])
# def start_feature_ranking(project_id):
#     task_name = "feature_ranking"
#     request_data_json = request.get_json()
#     kpi_list = request_data_json.get("kpi_list", [])  # Other KPIs list
#     important_features = request_data_json.get("important_features", [])
#     kpi = request_data_json.get("kpi", None)

#     project = project_model.collection.find_one({"_id": project_id})

#     if not project:
#         return jsonify({"error": "Invalid Project ID"}), 400

#     directory_project = directory_project_path_full(project_id, [])
#     if not os.path.isdir(directory_project):
#         return jsonify({"error": "Invalid Project ID"}), 400

#     if not os.path.isfile(os.path.join(directory_project, filename_raw_data_csv())):
#         return jsonify({"message": "Data set not uploaded"}), 400

#     if not kpi:
#         return jsonify({"error": "Missing 'kpi' in request"}), 400

#     task_params = {"project_id": project_id, "kpi": kpi, "task_name": task_name}
#     task_key = generate_task_key(**task_params)

#     existing_task_id = redis_client.get(task_key)
#     if existing_task_id:
#         return (
#             jsonify(
#                 {
#                     "message": "Task is already running",
#                     "task_id": existing_task_id.decode(),
#                     "project_id": project_id,
#                 }
#             ),
#             200,
#         )

#     result = async_optimised_feature_rank.apply_async(
#         args=[kpi, kpi_list, important_features, directory_project],  # Passing positional arguments
#         kwargs={
#             "project_id": project_id,
#             "task_key": task_key,
#         },  # Passing project_id as a keyword argument
#     )

#     # Store task metadata in Redis
#     task_info = {
#         "task_id": result.id,
#         "status": "pending",
#         "project_id": project_id,
#         "kpi": kpi,
#         "important_features": important_features,
#         "kpi_list": kpi_list,
#         "start_time": datetime.now().isoformat(),
#         "params": task_params,
#     }
#     redis_client.hset("running_feature_ranking_tasks", result.id, json.dumps(task_info))

#     # Update MongoDB with task info
#     project_model.add_task_metadata(project_id, result.id, task_info)

#     redis_client.setex(
#         task_key, current_app.config.get("REDIS_TIMEOUT_TASK_ID"), f"task:{result.id}"
#     )  # Key expires time

#     return (
#         jsonify(
#             {
#                 "message": "Feature Ranking has started",
#                 "task_id": str(result.id),
#                 "task Id exists": existing_task_id,
#                 "project_id": project_id,
#             }
#         ),
#         202,
#     )
