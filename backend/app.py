from flask import Flask, request, jsonify, abort, g
from config import Configuration
import time

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
CORS(app)
app.config.from_object(Configuration)


db = SQLAlchemy(app)
migrate = Migrate(app, db)

auth = HTTPBasicAuth()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String())

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_auth_token(self, expires_in = 600):
        return jwt.encode(
            { 'id': self.id, 'exp': time.time() + expires_in }, 
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
            algorithm=['HS256'])
        except:
            return 
        return User.query.get(data['id'])

@auth.verify_password
def verify_password(username_or_token, password):
    # first try token
    user = User.verify_auth_token(username_or_token)
    # then check for username and password pair
    if not user:
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/api/register', methods=['POST'])
def register():
    username = request.json.get('email') 
    password = request.json.get('password')
    # Check for blank requests
    if username is None or password is None:
        abort(400)
    # Check for existing users
    if User.query.filter_by(username = username).first() is not None:
        abort(400)
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'id': user.id, 'username': user.username}), 201)


@app.route('/api/login', methods=['GET'])
@auth.login_required
def get_token():
    token = g.user.generate_auth_token(600)
    return jsonify({ 'token': token.decode('ascii'), 'duration': 600 })


@app.route('/api/user', methods=['GET'])
@auth.login_required
def user():
    return jsonify({ 'message':'Logged in user: {}'.format(g.user.username) })

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({ 'message':'world'})

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