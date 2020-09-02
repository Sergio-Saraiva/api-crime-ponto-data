from app import db
from passlib.hash import sha256_crypt
import jwt
import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True)
    password = db.Column(db.String())

    def __init__(self, email, password):
        self.email = email
        self.password = sha256_crypt.encrypt(password)

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'email': self.email,
            'password': self.password,

        }
    
    def check_password(self, password):
        if sha256_crypt.verify(password, self.password) :
            return True
        else:
            return False

    def encode_auth_token(self, user_id):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': self.id
            }
            return jwt.encode(
                payload,
                'f17c92d8ac77d7785a681180dd759259',
                algorithm='HS256'
            )
        except Exception as e:
            return e