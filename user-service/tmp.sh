curl -X 'PUT' \
  'http://localhost:8000/api/v1/users/profile' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "phoneNumber": "+12345678",
  "address": null
}' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNjMyM2IyMi0wN2UyLTQ1OGEtYThkMy03MGQxNWUxOWQyMmMiLCJleHAiOjE3NDI1NjgyMzR9.n_sOpRIPj0V8IC59DLSA67CYnST2yLPsj4QuBW7Lbug'
