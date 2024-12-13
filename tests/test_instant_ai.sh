HOST=127.0.0.1:8009
echo $HOST

curl $HOST/create-project

curl $HOST/upload -F "project_id=b1356c05-7195-497d-91f4-55549fc4ee04"

curl $HOST/process/upload -F "project_id=b1356c05-7195-497d-91f4-55549fc4ee04" -F "file=@cleaned_data.csv"

a=e266a080-d625-4565-9cf2-0f6c1e1c661f

curl $HOST/process/check-task/$a

curl $HOST/validator -H "Content-Type: application/json" -d '{ "project_id": "b1356c05-7195-497d-91f4-55549fc4ee04" }'

curl $HOST/list-column -H "Content-Type: application/json" -d '{ "project_id": "b1356c05-7195-497d-91f4-55549fc4ee04" }'

curl $HOST/process/drop-column -H "Content-Type: application/json" -d '{ "project_id": "b1356c05-7195-497d-91f4-55549fc4ee04", "column": ["reversed","referred_by","locality"] }'

curl $HOST/list-column -H "Content-Type: application/json" -d '{ "project_id": "b1356c05-7195-497d-91f4-55549fc4ee04" }'

curl $HOST/process/pre-process -H "Content-Type: application/json" -d '{ "project_id": "b1356c05-7195-497d-91f4-55549fc4ee04" }'

a=8346d8ec-6f0d-464f-96ca-662e9c533a7b
curl $HOST/process/check-task/$a

curl $HOST/process/feature-ranking -H "Content-Type: application/json" -d '{ "project_id": "b1356c05-7195-497d-91f4-55549fc4ee04","target_vars_list": ["reading_fee_paid", "Number_of_Months", "Coupon_Discount", "num_books", "magazine_fee_paid", "Renewal_Amount", "amount_paid"], "target_var": "amount_paid" }'

curl $HOST/process/check-task/$a


curl $HOST/process/cluster -H "Content-Type: application/json" -d '{ "project_id": "b1356c05-7195-497d-91f4-55549fc4ee04","target_var": "amount_paid", "level": 0, "path": [] }'


curl $HOST/process/cluster -H "Content-Type: application/json" -d '{ "project_id": "b1356c05-7195-497d-91f4-55549fc4ee04","target_var": "amount_paid", "level": 0, "path": [] }'
a=929dabf4-48d4-46f3-afd0-8cc0b7640b8c

curl $HOST/process/check-task/$a

curl $HOST/summerising -H "Content-Type: application/json" -d '{ "project_id": "b1356c05-7195-497d-91f4-55549fc4ee04","target_var": "amount_paid", "level": 0, "path": []  }'

