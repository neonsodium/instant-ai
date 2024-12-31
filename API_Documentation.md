# API Documentation

**Host:** `http://127.0.0.1:8009`

---

## **Create a New Project**

- **Endpoint:** `/projects/`
- **Method:** `POST`
- **Description:** Creates a new project and returns the project ID.
- **Parameters:**
  - `name` (string): Name of the Project.
  - `description` (String): Description of the Project.
- **Example:**

  ```bash
  curl -X POST http://127.0.0.1:8009/projects/ -H "Content-Type: Application/json" --data '{"name": "test","description": "test"}'
  ```

## **List all Projects**

- **Endpoint:** `/projects/`
- **Method:** `GET`
- **Description:** List all projects and returns the project IDs.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/
  ```

## **Check Project Status**

- **Endpoint:** `/projects/<project_id>/status`
- **Method:** `GET`
- **Description:** Retrieves the current status of a project, including whether data has been uploaded, feature ranking is completed, and clustering has started.
- **Example:**

  ```bash
  curl -X GET http://127.0.0.1:8009/projects/PROJECT_ID/status
  ```

## **Process Uploaded File**

- **Endpoint:** `/projects/<project_id>/files/upload`
- **Method:** `POST`
- **Description:** Processes the uploaded file for the given project.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `file` (file): File to process.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/files/upload -F "file=@data.csv"
  ```

---

## **Check Task Status**

- **Endpoint:** `/projects/tasks/<task_id>/status`
- **Method:** `GET/POST`
- **Description:** Checks the status of a task by task ID.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/tasks/TASK_ID/status
  ```

---

## **Validate Dataset**

- **Endpoint:** `/projects/<project_id>/dataset/validate`
- **Method:** `GET/POST`
- **Description:** Validates the uploaded dataset for a given project.
- **Parameters:**
  - `project_id` (string): ID of the project.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/dataset/validate
  ```

---

## **List Columns**

- **Endpoint:** `/projects/<project_id>/dataset/columns`
- **Method:** `GET/POST`
- **Description:** Lists the columns in the dataset for the specified project.
- **Parameters:**
  - `project_id` (string): ID of the project.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/dataset/columns
  ```

---

## **Drop Columns**

- **Endpoint:** `/projects/<project_id>/dataset/columns/drop`
- **Method:** `POST`
- **Description:** Drops specified columns from the dataset for the given project.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `column` (array): List of column names to drop.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["col1", "col2"] }'
  ```

---

## **Feature Ranking**

- **Endpoint:** `/projects/<project_id>/features/ranking`
- **Method:** `POST`
- **Description:** Ranks features based on their importance.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `kpi_list` (array): List of other KPIs variables.
  - `important_features` (array): List of user added features.
  - `kpi` (string): The target KPI for feature ranking.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/features/ranking -H "Content-Type: application/json" -d '{ "kpi_list": ["kpi1", "kpi2"] "important_features":["var1", "var2"] "kpi": "kpi" }'
  ```

---

## **Clustering**

- **Endpoint:** `/projects/<project_id>/clusters/subcluster`
- **Method:** `POST`
- **Description:** Performs clustering on the dataset.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `kpi` (string): Variable to cluster.
  - `level` (int): Clustering level.
  - `path` (array): Path of the clustering hierarchy.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/clusters/subcluster -H "Content-Type: application/json" -d '{ "kpi": "kpi", "level": 0, "path": [] }'
  ```

---

## **Summarize Clusters**

- **Endpoint:** `/projects/<project_id>/clusters/summarize`
- **Method:** `POST`
- **Description:** Summarizes the clustering results.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `level` (int): Clustering level.
  - `path` (array): Path of the clustering hierarchy.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/clusters/summarize -H "Content-Type: application/json" -d '{ "level": 0, "path": [] }'
  ```

---

## **Download Cluster Data**

- **Endpoint:** `/projects/<project_id>/clusters/download`
- **Method:** `POST`
- **Description:** Download the sub clustering results as a csv file.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `level` (int): Clustering level.
  - `path` (array): Path of the clustering hierarchy.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/clusters/download -H "Content-Type: application/json" -d '{ "level": 2, "path": [1,2] }'
  ```

---

## **Time Series Graph

- **Endpoint:** `/projects/<project_id>/time-series/encode`
- **Method:** `POST`
- **Description:** Service site trend graph of the time series
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `level` (int): Clustering level.
  - `path` (array): Path of the clustering hierarchy.
  - `user_added_vars_list` (list): User added target variables.
  - `no_of_months` (int): Number of months to predict.
  - `date_column` (string): Name of date column in the dataset.
  - `increase_factor` (int): Name of date column in the dataset.
  - `zero_value_replacement` (int): Zero value Replacement.
- **Example:**

  ```bash
  curl -X POST http://127.0.0.1:8009/projects/PROJECT_ID/time-series/encode -H "Content-Type: application/json" -d '{
    "user_added_vars_list": ["var1", "var2"],
    "level": 2,
    "path": [0, 1],
    "kpi": "sales",
    "no_of_months": 6,
    "date_column": "date",
    "increase_factor": 1.2,
    "zero_value_replacement": 0 }'
    
    ```

---

## **Time Series: Get encoded Columns

- **Endpoint:** `/projects/<project_id>/time-series/encoded-columns`
- **Method:** `POST`
- **Description:** Service site trend graph of the time series
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `level` (int): Clustering level.
  - `path` (array): Path of the clustering hierarchy.
  - `column_name` (String): Name of the column.
- **Example:**

  ```bash
  http://localhost:8009/projects/PROJECT_ID/time-series/encoded-columns \
  -H "Content-Type: application/json" \
  -d '{
        "level": 1,
        "path": [1],
        "column_name": "Material"
      }'
    
    ```

---

## **Time Series: Get Catagorical Columns

- **Endpoint:** `/projects/<project_id>/time-series/categorical-columns`
- **Method:** `POST`
- **Description:** Service site trend graph of the time series
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `level` (int): Clustering level.
  - `path` (array): Path of the clustering hierarchy.
  - `column_name` (String): Name of the column.
- **Example:**

  ```bash
  http://localhost:8009/projects/PROJECT_ID/time-series/categorical-columns \
  -H "Content-Type: application/json" \
  -d '{
        "level": 1,
        "path": [1],
      }'
    
    ```

---

### Notes

- Replace `PROJECT_ID` and `TASK_ID` with appropriate values for your project.
