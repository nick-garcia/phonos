from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from phonos import app, login
from werkzeug.security import generate_password_hash, check_password_hash

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

    admin = User()
    admin.username = 'admin'
    admin.password = generate_password_hash('admin')
    admin.is_admin = True
    db.session.add(admin)

    db.session.commit()


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


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

group_membership_table = db.Table('group_membership',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    groups = db.relationship('Group', secondary=group_membership_table, backref=db.backref('users'))

    def valid_password(self, password):
        return check_password_hash(self.password, password)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False, default='')

db.Index('user_username_password_idx', User.username, User.password)
