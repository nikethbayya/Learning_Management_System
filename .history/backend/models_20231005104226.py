from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String())
    firstName = db.Column(db.String(120))
    lastName = db.Column(db.String(120))
    security_question = db.Column(db.String(120))
    security_answer = db.Column(db.String(120))

    def verify_password(self, password):
        return check_password_hash(self.password, password)
    
    def verify_security_question(self, ans):
        return self.security_answer == ans

class PasswordRecovery(db.Model):
    __tablename__ = 'password_recovery'
    email = db.Column(db.String(120), unique=True, primary_key = True)
    token = db.Column(db.Text)

