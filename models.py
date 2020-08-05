import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import json

db = SQLAlchemy()
database_path = os.environ['DATABASE_URL']


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

class Receipt(db.Model):
    __tablename__ = 'receipt'

    id = Column(Integer, primary_key=True)
    number = Column(String)
    date = Column(date)
    issuer = Column(String)
    services = Column(db.array)
    total_amount = Column(float)
    paid_amount = Column(float)

    def __init__(self, number, issuer, services, total_amount):
        self.number = number
        self.date = date.now() #https://www.programiz.com/python-programming/datetime/current-datetime
        self.issuer = issuer
        self.services = services
        self.total_amount = total_amount
    
    def format(self):
        return {
            'id': self.id,
            'date': self.date.strftime("%d/%m/%Y %H:%M:%S"),
            'issuer': self.issuer,
            'services': self.services,
            'total_amount': self.total_amount,
            'paid_amount': self.paid_amount,
        }
