
from sqlalchemy import Column, String, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
import datetime

database_name = "getoutdoors"
database_path = "postgres://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()

class DBHelper:
    @staticmethod
    def insert(element, isTest=False):
        element.isTest = isTest
        db.session.add(element)
        db.session.commit()
    
    @staticmethod
    def update():
        db.session.commit()

    @staticmethod
    def delete(element):
        db.session.delete(element)
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()
  
    @staticmethod
    def close():
        db.session.close()


class Base(db.Model):
    __abstract__ = True
    isTest = db.Column(db.Boolean)

class Entity(Base):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    url = db.Column(db.String)


'''
Task
'''
class Task(Entity):
    __tablename__ = 'tasks'

    state = db.Column(db.String)
    country = db.Column(db.String)
    tags = db.Column(db.String)

'''
Series
'''
class Series(Entity):
    __tablename__ = 'series'
    tags = db.Column(db.String)

'''
Challenges
'''
class Challenge(Base):
    __tablename__ = 'challenges'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'))


    task = db.relationship("Task", backref=db.backref("challenges"))
    series = db.relationship("Series", backref=db.backref("challenges"))

'''

Ignore the tables below
Users
'''
class User(Entity):
    __tablename__ = 'users'


'''
Activities
'''
class Activity(Entity):
    __tablename__ = 'activities'
    date = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    user =  db.relationship("User", backref=db.backref("users"))


'''
Accomplishment
'''
class Accomplishment(Base):
    __tablename__ = 'accomplishments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))

    activity = db.relationship("Activity", backref=db.backref("accomplishments"))
    task = db.relationship("Task", backref=db.backref("accomplishments"))
   