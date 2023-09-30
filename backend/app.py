import json
from config import Configuration


# Libraries
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity
from flask_jwt_extended import unset_jwt_cookies, jwt_required, JWTManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Configuration)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
cors = CORS(app, origins=[app.config["CROSS_ORIGIN_URL"]])
db = SQLAlchemy(app)
jwt = JWTManager(app)


from models import User

@app.route('/')
def hello():
    return make_response(jsonify({"status": "RUNNING"}), 200)


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@app.route('/login', methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    # Handle Missing email or password

    if email == "" or password == "":
        return {"msg": "Please verify email and password fields."}, 401

    # ToDo: Check user data against db

    if email != "test" or password != "test":
        return {"msg": "Wrong email or password"}, 401

    access_token = create_access_token(identity=email)
    response = {"access_token": access_token}
    return response


@app.route("/resetPassword", methods=["POST"])
def resetPassword():
    data = request.json
    email = data["email"]

    # ToDo Send Email to Update Password
    # ToDo Update Password in Database
    # Should I be recieving a secret question response?


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data["email"]
    password = data["password"]
    password2 = data["password2"]
    firstName = data["firstName"]
    lastName = data["lastName"]
    secQuestion = data["secQuestion"]
    secAnswer = data["secAnswer"]

    expected_keys = ["email", "password", "password2",
                     "firstName", "lastName", "secQuestion", "secAnswer"]

    # Handle Missing Fields
    if any(key not in data or data[key] == "" for key in expected_keys):
        return {"msg": "Please enter all fields."}, 401

    # Handle Mismatched Passwords
    if password != password2:
        return make_response({"msg": "Please verify that your passwords match."}, 401)

    db.session.add(
        User(
            email=email, 
            password=password, 
            firstName=firstName,
            lastName=lastName,
            secQuestion=secQuestion,
            secAnswer=secAnswer
        )
    )
    db.session.commit()

    return make_response({"msg": "user created"}, 200)


@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    data = request.json
    email = data["email"]

    # Handle No Email
    if email == "":
        return make_response({"msg": "Please verify that your passwords match."}, 401)

    # ToDo Pull UserData from DataBase


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@app.cli.command('resetdb')
def resetdb_command():
    """Destroys and creates the database + tables."""
    DB_URL = Configuration.SQLALCHEMY_DATABASE_URI
    from sqlalchemy_utils import database_exists, create_database, drop_database
    if database_exists(DB_URL):
        print('Deleting database.')
        drop_database(DB_URL)
    if not database_exists(DB_URL):
        print('Creating database.')
        create_database(DB_URL)
    print('Creating tables.')
    db.create_all()
    print('Shiny!')
