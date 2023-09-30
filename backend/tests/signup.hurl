POST http://127.0.0.1:8000/register
{
  "email": "srvemu@iu.edu",
  "password": "srvemu",
  "password2": "srvemu",
  "firstName": "srvemu",
  "lastName": "srvemu",
  "secQuestion": "What is your pet name?",
  "secAnswer": "kabu"
}
HTTP 200
[Asserts]
jsonpath "$.msg" == "user created"