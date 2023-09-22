# Backend

## Install modules

```
pip freeze > requirements.txt
pip install -r requirements.txt
```

## Run flask

```
flask run --debug -p 8080
```

## Production

```
gunicorn -w 4 'app:app'
```

## References

https://medium.com/@anubabajide/rest-api-authentication-in-flask-481518a7479b
https://github.com/miguelgrinberg/REST-auth/blob/2904b70ea95885bc523e472e58e934925f1ab1eb/api.py