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
    street_address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(15))
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
    country = db.relationship("Country")
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship("Person", backref="numbers", lazy="joined")
    extra = db.Column(db.JSON)  # Extra information will change based on type.


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50))

db.Index('person_firstname_lastname_idx', Person.firstname, Person.lastname)


class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(2), nullable=False)
