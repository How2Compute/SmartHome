"""
Database Models Library
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Model to store information about devices
class Device(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text)
    api_key = db.Column(db.Text)
    active = db.Column(db.Boolean, default=False)
    access_level = db.Column(db.Integer)
    status = db.Column(db.Integer)
    
    def __init__(self, name, permission_level):
        self.name = name
        self.access_level = permission_level
        self.api_key = generate_api_token()

# Down here to avoid issues with circular dependancies
from helpers import generate_api_token

# Model to store notifications   
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer)
    category = db.Column(db.Text)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    callback_url = db.Column(db.Text)
    dismissed = db.Column(db.Boolean, default=0)
    
    # NOTE -120 -> all admins (also TODO when implementing GUI)
    # NOTE -121 -> all users
    def __init__(self, user_id, category, title, body, callback_url):
        self.user_id = user_id
        self.category = category
        self.title = title
        self.body = body
        self.callback_url = callback_url
        

class Preference(db.Model):
    __tablename__ = 'preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    device_id = db.Column(db.Integer, db.ForeignKey('clients.id')) #TODO does this actually need to be a foreign key or does it merely add overhead?
    key = db.Column(db.Text)
    value = db.Column(db.Text)
    access_required = db.Column(db.Integer)
    
    def __init__(self, user_id, device_id, key, value, access_required):
        self.user_id = user_id
        self.device_id = device_id
        self.key = key
        self.value = value
        self.access_required = access_required
    

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.Text)
    password = db.Column(db.Text)
    last_login = db.Column(db.DateTime)
    create_date = db.Column(db.DateTime)
    access_level = db.Column(db.Integer)
    
    preferences = db.relationship('Preference', backref='user', lazy='joined')
    
    def __init__(self, username, password, access_level):
        self.username = username
        self.password = password
        self.access_level = access_level
