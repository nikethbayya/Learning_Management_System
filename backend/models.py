from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, index=True, unique=True)
    password = db.Column(db.Text)
    firstName = db.Column(db.String(10))
    lastName = db.Column(db.String(10))
    secQuestion = db.Column(db.Text)
    secAnswer = db.Column(db.String(20))
