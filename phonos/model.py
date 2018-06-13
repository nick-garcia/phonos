from flask_sqlalchemy import SQLAlchemy
from phonos import app

import csv
import enum

db = SQLAlchemy(app)

def initialize():
    db.drop_all()
    db.create_all()

    with open('phonos/data/ISO_Country_Codes.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for country in reader:
            row = Country()
            row.name = country['Name']
            row.code = country['Code']
            db.session.add(row)

    db.session.commit()

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
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50))


class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(2), nullable=False)