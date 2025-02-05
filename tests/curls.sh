
# curl http://127.0.0.1:8009/projects/
# curl -X POST http://127.0.0.1:8009/projects/ -H "Content-Type: Application/json" --data '{"name": "test","description": "test"}'
# curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/status

# curl -X POST http://127.0.0.1:8009/projects/ -H "Content-Type: Application/json" --data '{"name": "test","description": "test"}'
# {"project":{"_id":"7f14ab06-8247-48ac-8550-17171c516e7f","name":"test","description":"test","created_at":"2025-01-14T11:00:52.736997","updated_at":"2025-01-14T11:00:52.737011","clusters":[]},"status":"success","message":"Directory created successfully.","path":"/home/ubuntu/instant-ai/projects/7f14ab06-8247-48ac-8550-17171c516e7f"}

# curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/files/upload -F "file=@../../../../Downloads/cleaned_apar.csv"
# {"message":"File processing has started","task_id":"f8d9d885-2509-4047-a0e1-61868e4c418c","project_id":"7f14ab06-8247-48ac-8550-17171c516e7f"}

curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/status

curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/dataset/columns
curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/status

curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/dataset/columns/mapping -H "Content-Type: application/json" -d '{  "column_mapping": {      "Invoice No": "Invoice_Number",    "Order Date": "Order_Date",    "Net Value /KL (NET_VAL_KL)": "Net_Value_per_KL",    "Packing Cost /KL": "Packing_Cost_per_KL"  }}'
curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["IGST", "SGST","UGST", "CGST"] }'
curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/features/ranking -H "Content-Type: application/json" -d '{ "kpi_list": [], "important_features":[], "kpi": "Revenue" }'
sleep 100


curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["Employee"] }'
curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["REG_DESC"] }'
curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/status

curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["Month"] }'
curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/status

curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/features/ranking -H "Content-Type: application/json" -d '{ "kpi_list": [], "important_features":[], "kpi": "Revenue" }'
curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/status


curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/clusters/subcluster -H "Content-Type: application/json" -d '{ "kpi": "Revenue", "level": 0, "path": [] }' && curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/clusters/subcluster -H "Content-Type: application/json" -d '{ "kpi": "Revenue", "level": 0, "path": [] }'
curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/status

curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/time-series/analysis -H "Content-Type: application/json" -d '{ "user_added_vars_list": [], "path": [0], "kpi": "Revenue", "no_of_months": 3, "date_column": "Order Date", "increase_factor": 1.2 }'


curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/features/weight -H "Content-Type: application/json" -d '{ "kpi": "Revenue", "path": [0]}'
curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/features/weight/result -H "Content-Type: application/json" -d '{ "kpi": "Revenue", "path": [0]}'
curl http://127.0.0.1:8009/projects/7f14ab06-8247-48ac-8550-17171c516e7f/clusters/defination -H "Content-Type: application/json" -d '{ "kpi": "Revenue", "level": 0, "path": [0],"cluster_no":1 }'
# history | grep curl | awk '{$1=""; print substr($0,2)}'
