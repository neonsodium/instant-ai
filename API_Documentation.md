# API Documentation

**Host:** `http://127.0.0.1:8009`

---

## **1. Create a New Project**

- **Endpoint:** `/create-project`
- **Method:** `GET/POST`
- **Description:** Creates a new project and returns the project ID.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/create-project
  ```

## **2. Process Uploaded File**

- **Endpoint:** `/process/upload`
- **Method:** `POST`
- **Description:** Processes the uploaded file for the given project.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `file` (file): File to process.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/process/upload -d '{ "project_id": "PROJECT_ID" } -F "file=@data.csv"
  ```

---

## **3. Check Task Status**

- **Endpoint:** `/process/check-task/<task_id>`
- **Method:** `GET`
- **Description:** Checks the status of a task by task ID.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/process/check-task/TASK_ID
  ```

---

## **4. Validate Dataset**

- **Endpoint:** `/validator`
- **Method:** `POST`
- **Description:** Validates the uploaded dataset for a given project.
- **Parameters:**
  - `project_id` (string): ID of the project.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/validator -H "Content-Type: application/json" -d '{ "project_id": "PROJECT_ID" }'
  ```

---

## **5. List Columns**

- **Endpoint:** `/list-column`
- **Method:** `POST`
- **Description:** Lists the columns in the dataset for the specified project.
- **Parameters:**
  - `project_id` (string): ID of the project.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/list-column -H "Content-Type: application/json" -d '{ "project_id": "PROJECT_ID" }'
  ```

---

## **6. Drop Columns**

- **Endpoint:** `/process/drop-column`
- **Method:** `POST`
- **Description:** Drops specified columns from the dataset for the given project.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `column` (array): List of column names to drop.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/process/drop-column -H "Content-Type: application/json" -d '{ "project_id": "PROJECT_ID", "column": ["col1", "col2"] }'
  ```

---

## **7. Pre-process Dataset** \[deprecated\]

- **Endpoint:** `/process/pre-process`
- **Method:** `POST`
- **Description:** Initiates pre-processing for the uploaded dataset.
- **Parameters:**
  - `project_id` (string): ID of the project.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/process/pre-process -H "Content-Type: application/json" -d '{ "project_id": "PROJECT_ID" }'
  ```

---

## **8. Feature Ranking**

- **Endpoint:** `/process/feature-ranking`
- **Method:** `POST`
- **Description:** Ranks features based on their importance.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `target_vars_list` (array): List of potential target variables.
  - `target_var` (string): The target variable for ranking.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/process/feature-ranking -H "Content-Type: application/json" -d '{ "project_id": "PROJECT_ID", "target_vars_list": ["var1", "var2"], "target_var": "target_var" }'
  ```

---

## **9. Clustering**

- **Endpoint:** `/process/cluster`
- **Method:** `POST`
- **Description:** Performs clustering on the dataset.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `target_var` (string): Variable to cluster.
  - `level` (int): Clustering level.
  - `path` (array): Path of the clustering hierarchy.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/process/cluster -H "Content-Type: application/json" -d '{ "project_id": "PROJECT_ID", "target_var": "target_var", "level": 0, "path": [] }'
  ```

---

## **10. Summarize Clusters**

- **Endpoint:** `/summerising`
- **Method:** `POST`
- **Description:** Summarizes the clustering results.
- **Parameters:**
  - `project_id` (string): ID of the project.
  - `level` (int): Clustering level.
  - `path` (array): Path of the clustering hierarchy.
- **Example:**

  ```bash
  curl http://127.0.0.1:8009/summerising -H "Content-Type: application/json" -d '{ "project_id": "PROJECT_ID", "level": 0, "path": [] }'
  ```

---

### Notes

- Replace `PROJECT_ID` and `TASK_ID` with appropriate values for your project.
