from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Enum
from phonos import app

import enum

db = SQLAlchemy(app)

def initialize():
    db.drop_all()
    db.create_all()

class PhoneStatus(enum.Enum):
    active = "Active"
    inactive = "Inactive"
    available = "Available"
    hold = "Hold"

class PhoneNumber(db.Model):
    __tablename__ = "phone_number"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # (Avaya, Cisco, mobile)
    status = db.Column(db.Enum(PhoneStatus))

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)

