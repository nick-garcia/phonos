from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from phonos import app, login
from werkzeug.security import generate_password_hash, check_password_hash

import csv
import datetime
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
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    updated = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    number = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # (Avaya, Cisco, mobile)
    status = db.Column(db.Enum(PhoneStatus))
    street_address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(15))
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
    country = db.relationship("Country")
    assignee_id = db.Column(db.Integer, db.ForeignKey('phone_assignee.id'))
    assigned_to = db.relationship("PhoneAssignee", backref="numbers", lazy="joined")
    extra = db.Column(db.JSON)  # Extra information will change based on type.
    needs_review = db.Column(db.Boolean, index=True, default=False, nullable=False)


class PhoneAssignee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, index=True)

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

db.Index('user_username_password_idx', User.username, User.password)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False, default='')

class Settings(db.Model):
    settings_for = db.Column(db.String(30), primary_key=True)
    settings = db.Column(db.JSON)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(25), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    schedule = db.Column(db.String(50), nullable=False)
    hostname = db.Column(db.String(50), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))

class JobLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job = db.Column(db.Integer, db.ForeignKey('job.id'))
    execution_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    success = db.Column(db.Boolean)
    reason = db.Column(db.Text)
