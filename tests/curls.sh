
curl http://127.0.0.1:8009/projects/
# curl -X POST http://127.0.0.1:8009/projects/ -H "Content-Type: Application/json" --data '{"name": "test","description": "test"}'
curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/status

curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/files/upload -F "file=@../../../../Downloads/cleaned_apar.csv"
curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/status

curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/dataset/columns
curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/status

curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["IGST", "SGST","UGST", "CGST"] }'
curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/features/ranking -H "Content-Type: application/json" -d '{ "kpi_list": [] "important_features":[] "kpi": "Revenue" }'\n



curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["Employee"] }'
curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["REG_DESC"] }'
curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/status

curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/dataset/columns/drop -H "Content-Type: application/json" -d '{ "column": ["Month"] }'
curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/status

curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/features/ranking -H "Content-Type: application/json" -d '{ "kpi_list": [], "important_features":[], "kpi": "Revenue" }'
curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/status


curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/clusters/subcluster -H "Content-Type: application/json" -d '{ "kpi": "Revenue", "level": 0, "path": [] }' && curl http://127.0.0.1:8009/212b2f8e-bf50-4181-9779-231c64919de5/clusters/subcluster -H "Content-Type: application/json" -d '{ "kpi": "Revenue", "level": 0, "path": [] }'\n
curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/status

curl http://127.0.0.1:8009/projects/212b2f8e-bf50-4181-9779-231c64919de5/time-series/analysis -H "Content-Type: application/json" -d '{ "user_added_vars_list": [], "path": [0], "kpi": "Revenue", "no_of_months": 3, "date_column": "Order Date", "increase_factor": 1.2 }'


# history | grep curl | awk '{$1=""; print substr($0,2)}'
