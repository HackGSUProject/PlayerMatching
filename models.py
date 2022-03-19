from database import db
from flask_login import UserMixin

class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    Fname = db.Column(db.String(50), nullable=False)
    Lname = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(50), nullable=False)
    Pnumber = db.Column(db.String(50) , nullable=False)
    password = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    status = db.Column(db.Integer, nullable=False)
    discord = db.Column(db.String(50), nullable=False)


