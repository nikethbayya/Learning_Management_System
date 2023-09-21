from flask import Flask, redirect, url_for, request, make_response
from config import Configuration

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo


app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

print(Configuration.SQLALCHEMY_DATABASE_URI)

# Authentication
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Api
@auth.route('/')
def index():
    return 'Hello World'

@auth.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return make_response({"status": "success", "message": "user logged in already"}, 200)
    
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()
    print(user)
    print(user.check_password(password))
    if user is None or not user.check_password(password):
        return make_response({"status": "failure", "message": "incorrect username or password"}, 200)
    
    login_user(user, remember=False)
    return make_response({"status": "success", "message": "user found"}, 200)

@app.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return make_response({"status": "failure", "message": "user already logged in"}, 200)
    
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()
    if user is not None:
        return make_response({"status": "failure", "message": "user already present"}, 200)
    
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return make_response({"status": "success", "message": "user created"}, 200)

@app.route('/logout')
def logout():
    logout_user()
    return make_response({"status": "success", "message": "logged out"}, 200)

@app.route('/user')
def get_user_details():
    user = current_user
    print(user)
    return make_response({"status": "success", "message": "logged out"}, 200)


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


if __name__ == '__main__':
    # serve(app, host="0.0.0.0", port=8000, threads=100)
    app.run()