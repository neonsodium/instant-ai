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

## **Feature weight onehot encoded**

- **Endpoint:** `/projects/<project_id>/features/onehot`
- **Method:** `POST`
- **Description:** Ranks features based on their importance, Async.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `kpi` (string): The target KPI for feature ranking.
  - `path` (array): Path of the clustering hierarchy.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/features/onehot -H "Content-Type: application/json" -d '{ "path": [1,2,4]  "kpi": "kpi" }'
  ```

---

## **Feature weight onehot encoded Result**

- **Endpoint:** `/projects/<project_id>/features/weight/onehot`
- **Method:** `POST`
- **Description:** Result of Ranks features based on their importance.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `kpi` (string): The target KPI for feature ranking.
  - `path` (array): Path of the clustering hierarchy.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/features/weight/onehot -H "Content-Type: application/json" -d '{ "path": [1,2,4]  "kpi": "kpi" }'
  ```

---

## **Feature weight label encoded**

- **Endpoint:** `/projects/<project_id>/features/label`
- **Method:** `POST`
- **Description:** Ranks features based on their importance, Async.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `kpi` (string): The target KPI for feature ranking.
  - `path` (array): Path of the clustering hierarchy.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/features/label -H "Content-Type: application/json" -d '{ "path": [1,2,4]  "kpi": "kpi" }'
  ```

---

## **Feature weight label encoded Result**

- **Endpoint:** `/projects/<project_id>/features/weight/label`
- **Method:** `POST`
- **Description:** Result of Ranks features based on their importance.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `kpi` (string): The target KPI for feature ranking.
  - `path` (array): Path of the clustering hierarchy.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/features/weight/label -H "Content-Type: application/json" -d '{ "path": [1,2,4]  "kpi": "kpi" }'
  ```

---

## **Clustering**

- **Endpoint:** `/projects/<project_id>/clusters/subcluster`
- **Method:** `POST`
- **Description:** Performs clustering on the dataset.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `kpi` (string): Variable to cluster.
  - `path` (array): Path of the clustering hierarchy.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/clusters/subcluster -H "Content-Type: application/json" -d '{ "kpi": "kpi", "path": [] }'
  ```

---

## **Clustering Defination**

- **Endpoint:** `/projects/<project_id>/clusters/defination`
- **Method:** `POST`
- **Description:** Some cluster defination.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `kpi` (string): The target KPI for feature ranking.
  - `path` (array): Path of the clustering hierarchy.
  - `cluster_no` (int): The Cluster number to be selected.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/clusters/defination -H "Content-Type: application/json" -d '{ "path": [1,2,4]  "kpi": "kpi", "cluster_no": 3}'
  ```

  ---

## **Summarize Clusters**

- **Endpoint:** `/projects/<project_id>/clusters/summarize`
- **Method:** `POST`
- **Description:** Summarizes the clustering results.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `path` (array): Path of the clustering hierarchy.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/clusters/summarize -H "Content-Type: application/json" -d '{ "path": [] }'
  ```

---

## **Download Cluster Data**

- **Endpoint:** `/projects/<project_id>/clusters/download`
- **Method:** `POST`
- **Description:** Download the sub clustering results as a csv file.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `path` (array): Path of the clustering hierarchy.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/projects/PROJECT_ID/clusters/download -H "Content-Type: application/json" -d '{ "path": [1,2] }'
  ```

---

## **Time Series Graph

- **Endpoint:** `/projects/<project_id>/time-series/analysis`
- **Method:** `POST`
- **Description:** Service site trend graph of the time series
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `path` (array): Path of the clustering hierarchy.
  - `kpi` (string): The target KPI for Time series Analysis.
  - `no_of_months` (int): Number of months to predict.
  - `date_column` (string): Name of date column in the dataset.
  - `adjustments` (dict): adjustments = {
    'security_deposit': "+23%",
    'branch_name_HSR Layout': "+5",
    'num_books': "+2"}.
- **Example:**

  ```bash
  curl -X POST http://127.0.0.1:8009/projects/PROJECT_ID/time-series/analysis -H "Content-Type: application/json" -d '{
    "path": [0, 1],
    "kpi": "sales",
    "no_of_months": 6,
    "date_column": "date",
    "adjustments" : {
    "security_deposit": "+23%",        
    "branch_name_HSR Layout": "+5",    
    "num_books": "+2"      } }',
    
    
    ```

---

## **Time Series: Get Encoded Columns**

- **Endpoint:** `/projects/<project_id>/time-series/encoded-columns`
- **Method:** `POST`
- **Description:** Retrieves a list of all the encoded categories for a categorical column, which are used as input for time-series Graph user_added_vars_list.
- **Parameters:**
  - `project_id` (string): The ID of the project.
  - `path` (array): The path of the clustering hierarchy.
  - `column_name` (string): The name of the column.
- **Example:**

  ```bash
  curl -X POST http://localhost:8009/projects/PROJECT_ID/time-series/encoded-columns \
  -H "Content-Type: application/json" \
  -d '{
        "path": [1],
        "column_name": "Material"
      }'
  ```

---

## **Time Series: Get Categorical Columns**

- **Endpoint:** `/projects/<project_id>/time-series/categorical-columns`
- **Method:** `POST`
- **Description:** Retrieves a list of all categorical columns, which are used as input for encoded columns.
- **Parameters:**
  - `project_id` (string): The ID of the project.
  - `path` (array): The path of the clustering hierarchy.
- **Example:**

  ```bash
  curl -X POST http://localhost:8009/projects/PROJECT_ID/time-series/categorical-columns \
  -H "Content-Type: application/json" \
  -d '{
        "path": [1]
      }'
  ```

---
Here’s the revised request and response explanation:

---

## **Get Running Tasks**

- **Endpoint:** `/projects/tasks/running`
- **Method:** `GET`
- **Description:** Retrieves a list of currently running tasks within the system.

### **Request Example**

```bash
curl http://localhost:8080/projects/tasks/running
```

---

This allows users to track ongoing tasks and their associated metadata.

Here’s a cleaned-up version of your Markdown content for better readability and consistency:

---

## **MySQL DB Connect**

- **Endpoint:** `/projects/<project_id>/dataset/connector`
- **Method:** `POST`
- **Description:**  
  Connect to the database and convert the specified table to a CSV file, bypassing the upload method. **Note:** This feature does not work on Cloud.
- **Parameters:**
- `project_id` (string): The ID of the project.
- `db_config` (object): Database connection configuration, including:
  - `host` (string): The database host.
  - `user` (string): The username for database authentication.
  - `password` (string): The password for database authentication.
  - `database` (string): The name of the database.
- `table` (string): The name of the table to export.

### **Example**

```bash
curl -X POST http://localhost:8009/projects/PROJECT_ID/dataset/connector \
-H "Content-Type: application/json" \
-d '{
  "db_config": {
      "host": "localhost",
      "user": "your_username",
      "password": "your_password",
      "database": "your_database"
  },
  "table": "your_table_name"
}'
```

---

## **Column Mapping**

- **Endpoint:** `/projects/<project_id>/dataset/columns/mapping`
- **Method:** `POST`
- **Description:**  
  Map or rename columns within a dataset.
- **Parameters:**
- `project_id` (string): The ID of the project.
- `column_mapping` (object): Key-value pairs mapping original column names to their new names.

- **Example:**

```bash
curl -X POST http://localhost:8009/projects/PROJECT_ID/dataset/columns/mapping \
-H "Content-Type: application/json" \
-d '{
  "column_mapping": {
      "COLUMN1": "RENAMED_COLUMN1",
      "COLUMN2": "RENAMED_COLUMN2",
      "COLUMN3": "RENAMED_COLUMN3",
      "COLUMN4": "RENAMED_COLUMN4"
  }
}'
```

---

This version improves clarity and formatting while keeping the information intact.

### Notes

- Replace `PROJECT_ID` with the appropriate project ID for your use case.
