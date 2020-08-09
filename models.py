from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os
import datetime
import json

db = SQLAlchemy()
database_path = os.environ['DATABASE_URL']


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class Cases(db.Model):
    __tablename__ = 'cases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String)
    date = Column(DateTime)
    issuer = Column(String)
    services = db.relationship('Services', backref='cases',
                               cascade="all, delete, delete-orphan")
    total_amount = Column(Float)
    paid = Column(Boolean)

    def __init__(self, number, issuer, total_amount):
        self.number = number
        self.date = datetime.datetime.now()
        self.issuer = issuer
        # self.services = services
        self.total_amount = total_amount

    def format(self):
        return {
            'id': self.id,
            'number': self.number,
            'date': self.date.strftime("%d/%m/%Y %H:%M:%S"),
            'issuer': self.issuer,
            'services': [service.format() for service in self.services],
            'total_amount': self.total_amount,
            'paid': self.paid,
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Services(db.Model):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, db.ForeignKey('cases.id'))
    description = Column(String)
    amount = Column(Float)
    quantity = Column(Integer)

    def __init__(self, description, amount, quantity):
        # self.case_id = case_id
        self.amount = amount
        self.description = description
        self.quantity = quantity

    def format(self):
        return {
            'case_id': self.case_id,
            'amount': self.amount,
            'quantity': self.quantity,
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Donors(db.Model):
    __tablename__ = 'donors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    montly_limit = Column(Float)

    def __init__(self, name, montly_limit=None):
        self.name = name
        self.montly_limit = montly_limit

    def format(self):
        return {
            'name': self.name,
            'montly_limit': self.montly_limit,
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Donations(db.Model):
    __tablename__ = 'donations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, db.ForeignKey('cases.id'))
    donor_id = Column(Integer, db.ForeignKey('donors.id'), nullable=True)
    paid_amount = Column(Float)

    def __init__(self, case_id, paid_amount, donor_id=None):
        self.case_id = case_id
        self.donor_id = donor_id
        self.paid_amount = paid_amount

    def format(self):
        return {
            'case_id': self.case_id,
            'donor_id': self.donor_id,
            'paid_amount': self.paid_amount
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
