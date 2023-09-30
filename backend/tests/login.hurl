# Wrong password
POST http://127.0.0.1:8000/login
{
  "email": "test",
  "password": "wrong"
}
HTTP 401

POST http://127.0.0.1:8000/login
{
  "email": "test",
  "password": "test"
}
HTTP 200
[Asserts]
jsonpath "$.access_token" exists