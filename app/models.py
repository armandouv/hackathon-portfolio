from flask_login import UserMixin
from . import db

"""
class User(db.Model):
    id = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))"""


class UserModel(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    firstname = db.Column(db.String(1000))
    lastname = db.Column(db.String(1000))
    password = db.Column(db.String(100))
    '''
    __tablename__ = "users"

    username = db.Column(db.String(), primary_key=True)
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User {self.username}>"'''


class UserModel(UserMixin, db.Model):
    __tablename__ = "post"
    id_post = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    title = db.Column(db.String(100))
    text = db.Column(db.String(1000))
    creation_date = db.Column(db.DateTime)
    modification_date = db.Column(db.DateTime)
    created_by = db.Column(db.ForeignKey("users.id"))
