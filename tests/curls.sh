
# curl http://127.0.0.1:8009/projects/
# curl -X POST http://127.0.0.1:8009/projects/ -H "Content-Type: Application/json" --data '{"name": "test","description": "test"}'
# curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/status

# curl -X POST http://127.0.0.1:8009/projects/ -H "Content-Type: Application/json" --data '{"name": "test","description": "test"}'
# {"project":{"_id":"df274957-cb1c-44c8-91af-e5f4cd4f9ce5","name":"test","description":"test","created_at":"2025-01-14T11:00:52.736997","updated_at":"2025-01-14T11:00:52.737011","clusters":[]},"status":"success","message":"Directory created successfully.","path":"/home/ubuntu/instant-ai/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5"}

# curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/files/upload -F "file=@../../../../Downloads/cleaned_apar.csv"
# {"message":"File processing has started","task_id":"f8d9d885-2509-4047-a0e1-61868e4c418c","project_id":"df274957-cb1c-44c8-91af-e5f4cd4f9ce5"}

curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/status

curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/dataset/columns
curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/status

curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["IGST", "SGST","UGST", "CGST"] }'
curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/features/ranking -H "Content-Type: application/json" -d '{ "kpi_list": [], "important_features":[], "kpi": "Revenue" }'
sleep 100


curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["Employee"] }'
curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["REG_DESC"] }'
curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/status

curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["Month"] }'
curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/status

curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/features/ranking -H "Content-Type: application/json" -d '{ "kpi_list": [], "important_features":[], "kpi": "Revenue" }'
curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/status


curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/clusters/subcluster -H "Content-Type: application/json" -d '{ "kpi": "Revenue", "level": 0, "path": [] }' && curl http://127.0.0.1:8009/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/clusters/subcluster -H "Content-Type: application/json" -d '{ "kpi": "Revenue", "level": 0, "path": [] }'\n
curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/status

curl http://127.0.0.1:8009/projects/df274957-cb1c-44c8-91af-e5f4cd4f9ce5/time-series/analysis -H "Content-Type: application/json" -d '{ "user_added_vars_list": [], "path": [0], "kpi": "Revenue", "no_of_months": 3, "date_column": "Order Date", "increase_factor": 1.2 }'


# history | grep curl | awk '{$1=""; print substr($0,2)}'
