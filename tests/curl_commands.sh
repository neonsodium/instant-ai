curl http://localhost:8009/create_new_project
project_id=5d1edd7f-b5b5-4939-9c80-8b40411b9bab

curl -X POST http://localhost:8009/upload -F "project_id=$project_id" -F "file=@jb_sales.csv"

task_id=cc9f24f6-aabd-4258-8274-ead98a9cd527
curl localhost:8009/check-task/$task_id

# note update teh project id
curl -X POST localhost:8009/process/feature_ranking -H "Content-Type: application/json" \
-d '{"target_vars_list": ["reading_fee_paid", "Number_of_Months", "Coupon_Discount", "num_books", "magazine_fee_paid", "Renewal_Amount", "amount_paid"],    "target_var": "amount_paid",    "level": 0, "project_id": "5d1edd7f-b5b5-4939-9c80-8b40411b9bab",    "path": []    }'

task_id=a750439e-7a79-4d11-8293-412a2577cbf2
curl localhost:8009/check-task/$task_id