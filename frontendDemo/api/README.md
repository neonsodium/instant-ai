# API Documentation for Cluster and Sub-cluster Data

This documentation outlines the available endpoints for the API hosted at http://ec2-18-61-145-241.ap-south-2.compute.amazonaws.com.

##1. Get Sub-cluster Data by Cluster Number

**Endpoint:**

`GET /sub_cluster/<cluster_number>`

**Description:**

Fetches sub-cluster data for a given cluster number.

**URL:**

`http://ec2-18-61-145-241.ap-south-2.compute.amazonaws.com/sub_cluster/<cluster_number>`


**Example Request:**

```bash
curl -X GET "http://ec2-18-61-145-241.ap-south-2.compute.amazonaws.com/sub_cluster/1"
```

##2. Post Sub-cluster Data

**Endpoint:**

`POST /sub_cluster`

**Description:**

Posts a request to retrieve data for a specific sub-cluster by providing the cluster number in the request body.

**URL:**

`http://ec2-18-61-145-241.ap-south-2.compute.amazonaws.com/sub_cluster`

```bash
curl -X POST "http://ec2-18-61-145-241.ap-south-2.compute.amazonaws.com/sub_cluster" \
-H "Content-Type: application/json" \
-d '{"cluster_number": 1}'
```

##3. Get All Cluster Data

**Endpoint:**

`GET /get_cluster_data`

**Description:**

Fetches all cluster data stored in the cluster_data.json file.

**URL:**

`http://ec2-18-61-145-241.ap-south-2.compute.amazonaws.com/get_cluster_data`

**Example Request:**

```bash
curl -X GET "http://ec2-18-61-145-241.ap-south-2.compute.amazonaws.com/get_cluster_data"
```























