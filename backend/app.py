import os
import pathlib
import requests
import secrets
import json
from config import Configuration
from flask import Flask, request, jsonify, make_response, session, redirect
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity
from flask_jwt_extended import unset_jwt_cookies, jwt_required, JWTManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from functools import wraps
from enum import Enum 

import google
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from flask_mail import Mail, Message

app = Flask(__name__)
app.config.from_object(Configuration)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
cors = CORS(app, origins=[app.config["CROSS_ORIGIN_URL"]])
jwt = JWTManager(app)
db = SQLAlchemy(app)
mail = Mail(app)

from models import User, PasswordRecovery, Enrollment, Courses, UserRole



# # Google oauth
# client_secrets_file = os.path.join(
#     pathlib.Path(__file__).parent, "client_secret.json")
# flow = Flow.from_client_secrets_file(
#     client_secrets_file=client_secrets_file,
#     scopes=[
#         "https://www.googleapis.com/auth/userinfo.profile",
#         "https://www.googleapis.com/auth/userinfo.email",
#         "openid",
#     ],
#     redirect_uri=Configuration.BACKEND_URL+"/auth/callback",
# )

@jwt_required()
def role_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_jwt_identity()
            
            # Assuming you have a way to determine the user's role, e.g., current_user["role"]
            user_role = user.role

            if user_role not in allowed_roles:
                return jsonify({"message": "Access denied. Insufficient role."}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


@app.route("/auth/google")
def login():
    authorization_url, state = flow.authorization_url()
    # Store the state so the callback can verify the auth server response.
    session["state"] = state
    return make_response(jsonify(auth_url=authorization_url), 200)

@app.route("/auth/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    request_session = requests.session()
    token_request = google.auth.transport.requests.Request(session=request_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token, request=token_request,
        audience=Configuration.GOOGLE_CLIENT_ID
    )
    email = id_info["email"]

    # If no user, create
    if User.query.filter_by(email=email).first() is None:
        firstName = id_info["given_name"]
        lastName = id_info["family_name"]
        db.session.add(
            User(
                email=email,
                password=generate_password_hash("dfacc40f8cd6597490ecb32ab413abf2b9e020c9f6780bce7551fa2697e34c67"),
                firstName=firstName,
                lastName=lastName
            )
        )
        db.session.commit()
    access_token = create_access_token(identity=email)
    return redirect(Configuration.FRONTEND_URL + '/loggedin?token=' + access_token)


@app.route('/')
def hello():
    return make_response({"status": "RUNNING"}, 200)


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


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data["email"]
    password = data["password"]
    # password2 = data["password2"]
    firstName = data["firstName"]
    lastName = data["lastName"]
    secQuestion = data["secQuestion"]
    secAnswer = data["secAnswer"]

    expected_keys = ["email", "password",
                     "firstName", "lastName", "secQuestion", "secAnswer"]

    # Handle Missing Fields
    if any(key not in data or data[key] == "" for key in expected_keys):
        return {"msg": "Please enter all fields."}, 401

    # # Handle Mismatched Passwords
    # if password != password2:
    #     return {"msg": "Please verify that your passwords match."}, 401


    if User.query.filter_by(email=email).first() is not None:
        # User already exists
        return make_response(jsonify(msg="user exists"), 401)

    db.session.add(
        User(
            email=email,
            password=generate_password_hash(password),
            firstName=firstName,
            lastName=lastName,
            security_question=secQuestion,
            security_answer=secAnswer
        )
    )
    db.session.commit()
    return make_response(jsonify(msg="user created"), 200)


@app.route('/login', methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    # Handle Missing email or password

    if email == "" or password == "":
        return {"msg": "Please verify email and password fields."}, 401

    # if email == "test" and password == "test":
    #     access_token = create_access_token(identity='test@iu.edu')
    #     response = {"access_token": access_token}

    #     return make_response(response, 200)

    user = User.query.filter_by(email=email).first()
    if user is None or not user.verify_password(password):
        return make_response(jsonify("Incorrect email or password"), 401)

    access_token = create_access_token(identity=email)
    response = {"access_token": access_token}
    return response

@app.route('/courseInfo', methods=["GET"])
@jwt_required()
def get_course_info():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()

    if not user:
        return make_response(jsonify(msg="user not found"), 401)
    
    userID = user.id
    userRole = user.role

    #If the user has the admin role he recieves all courseIDs
    if userRole == "Admin":
        enrollments = Enrollment.query.all()
        course_ids = [enrollment.course_id for enrollment in enrollments]
    else:
        enrollments = Enrollment.query.filter_by(student_id=userID).all()
        course_ids = [enrollment.course_id for enrollment in enrollments]

    response = {
    "courseInfo": {
        "studentID": user.id,
        "courseIDs": course_ids  
    }
}

    return make_response(jsonify(response), 200)
@app.route("/getAllUsers", methods=["GET"])
@jwt_required()
def getAllUsers():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if not user:
        return make_response(jsonify(msg="access denied"), 403)
    userRole = user.role
    if(userRole != UserRole.ADMIN):
        return make_response(jsonify(msg="user not authorized to retrieve this resource"), 403)
    users = User.query.all()
    userTable = {}
    loadIndex = 0
    for user in users:
        userTable[loadIndex] = {
            "id": user.id,
            "email": user.email,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "role": user.role.value
        }
        loadIndex += 1
    return make_response(jsonify({"userTable" :userTable}), 200)    
    
#returns all courses in school's system for admin view
@app.route('/getAllCourses', methods=['GET'])
@jwt_required()
def getAllCourses():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if not user:
        return make_response(jsonify(msg="user not found"), 401)
    
    userID = user.id
    userRole = user.role
    print(userRole)
    if(userRole != UserRole.ADMIN):
        return make_response(jsonify(msg="user not authorized"), 403)
    courses = Courses.query.all()
    tosend = {}
    for course in courses:
        tosend[course.id] = {"id":course.id,"description" : course.description,"courseNumber" : course.courseNumber, "instructor": course.instructor}
        
        
    return make_response(jsonify({"courses" : tosend}), 200)
    
    
@app.route('/deleteCourse', methods=["DELETE"])
#@role_required(["Admin"]) 
@jwt_required()
def deleteCourse():
    courseID = request.json.get("courseID", None)

    if courseID == "":
        return {"msg": "Please verify courseID"}, 401
    
    enrollments = Enrollment.query.filter_by(course_id=courseID).all()
    courses  = Courses.query.filter_by(id=courseID).all

    if not enrollments or not courses:
        return {"msg": "Could not find course."}, 401

    for enrollment in enrollments:
        db.session.delete(enrollment)
    
    for course in courses:
        db.session.delete(course)

    db.session.commit()
    return make_response(jsonify(msg="Course Deleted"), 200)

@app.route('/updateCourse', methods=["PUT"])
#@role_required(["Admin","Instructor"]) 
@jwt_required()
def updateCourse():
    courseID = request.json.get("courseID", None)
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    role = convert_user_role(str(user.role))
    data = request.json

    if role == "Instructor": 
        if "name" in data or "description" in data:
            course = Courses.query.filter_by(id=courseID).first()
            if course:
                # Assuming data contains 'name' and 'description' fields
                update_data = {}

                if "name" in data:
                    update_data['name'] = data["name"]
                else:
                    # If 'name' is not in data, retain the current value from the database
                    update_data['name'] = course.name

                if "description" in data:
                    update_data['description'] = data["description"]
                else:
                    # If 'description' is not in data, retain the current value from the database
                    update_data['description'] = course.description

                # Update the course with the new data
                course.name = update_data['name']
                course.description = update_data['description']

                # Update records in the Enrollment model with the corresponding courseID
                Enrollment.query.filter_by(course_id=courseID).update(update_data)
        else:
            return {"msg": "Please verify input fields."}, 401
    
    if role == "Instructor": 
        if "name" in data or "description" in data or "number" in data or "instructor" in data:
            course = Courses.query.filter_by(id=courseID).first()
            if course:
                # Assuming data contains 'name' and 'description' fields
                update_data = {}

                if "name" in data:
                    update_data['name'] = data["name"]
                else:
                    # If 'name' is not in data, retain the current value from the database
                    update_data['name'] = course.name

                if "description" in data:
                    update_data['description'] = data["description"]
                else:
                    # If 'description' is not in data, retain the current value from the database
                    update_data['description'] = course.description
                
                if "number" in data:
                    update_data['number'] = data["number"]
                else:
                    # If 'description' is not in data, retain the current value from the database
                    update_data['number'] = course.number
                
                if "instructor" in data:
                    update_data['instructor'] = data["instructor"]
                else:
                    # If 'description' is not in data, retain the current value from the database
                    update_data['instructor'] = course.instructor
                
                # Update the course with the new data
                course.name = update_data['name']
                course.description = update_data['description']
                course.number = update_data['number']
                course.number = update_data['instructor']

                # Update records in the Enrollment model with the corresponding courseID
                Enrollment.query.filter_by(course_id=courseID).update(update_data)
        else:
            return {"msg": "Please verify input fields."}, 401


    

    db.session.commit()
    return make_response(jsonify(msg="Course Updated"), 200)

@app.route('/updateStudents', methods=["PUT"])
#@role_required(["Admin","Instructor"]) 
@jwt_required()
def updateStudents():
    courseID = request.json.get("courseID", None)
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    role = convert_user_role(str(user.role))
    data = request.json

    #ToDo Need to write an update function for the Enrollments model
    #Need to discuss how to map teachers to their courses


    

    db.session.commit()
    return make_response(jsonify(msg="Course Updated"), 200)




@app.route('/userInfo', methods=["GET"])
@jwt_required()
def get_user_info():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    role = convert_user_role(str(user.role))
    if not user:
        return make_response(jsonify(msg="user not found"), 401)
    
    response = {
        "userInfo": {
            "firstName": user.firstName,
            "lastName": user.lastName,
            "role" : role,
        }
    }

    return make_response(jsonify(response), 200)

def convert_user_role(role_str):
    if role_str == 'UserRole.STUDENT':
        return 'Student'
    if role_str == 'UserRole.ADMIN':
        return 'Admin'
    if role_str == 'UserRole.INSTRUCTOR':
        return 'Instructor'
    return role_str


def create_reset_url(email):
    token = secrets.token_hex()
    db.session.add(
        PasswordRecovery(
            email=email,
            token=token
        )
    )
    db.session.commit()
    return Configuration.FRONTEND_URL + '/resetpassword?email=' + email + '&token=' + token

@app.route("/recoverPassword", methods=["POST"])
def recoverPassword():
    data = request.json
    email = data["email"]
    type = data["type"]

    # Already has reset url
    recover = PasswordRecovery.query.filter_by(email=email).first()
    if recover:
        url = Configuration.FRONTEND_URL + '/resetpassword?email=' + email + '&token=' + recover.token
        return make_response(jsonify(reset_url=url), 200)
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return make_response(jsonify(msg="user not found"), 401)

    if type == 'using_security_question':
        if 'security_answer' not in data:
            return make_response(jsonify(msg="secuirty answer missing"), 401)
        ans = data['security_answer']
        if not user.verify_security_question(ans):
            return make_response(jsonify(msg="incorrect security answer"), 401)
        return make_response(jsonify(reset_url=create_reset_url(email)), 200)
    elif type == 'using_email':
        print("email")
        # if account exists send mail
        send_mail(toMail=email, subject='Reset password', body=create_reset_url(email))
        return make_response(jsonify(msg="email sent"), 200)
    elif type == 'otp':
        print('otp')

    return make_response(jsonify(msg="invalid recovery type"), 401)

@app.route("/resetPassword", methods=["POST"])
def resetPassword():
    data = request.json
    email = data["email"]
    token = data["token"]
    password = data["password"]

    # verify the token
    record = PasswordRecovery.query.filter_by(email=email).filter_by(token=token).first()
    if not record:
        return make_response(jsonify(msg="incorrect token"), 401)
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return make_response(jsonify(msg="user not token"), 401)
    user.password = generate_password_hash(password)
    db.session.commit()

    # Delete password recovery record after resetting the password
    db.session.delete(record)

    return make_response(jsonify(msg="reset successful"), 200)


@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    return make_response(jsonify(msg="profile"), 200)


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return make_response(response, 200)

def send_mail(toMail, subject, body):
    print('mail sent')
    msg = Message(subject, sender= 'hoosierroom@gmail.com', recipients = [toMail])
    msg.body = body
    mail.send(msg)


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
