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
    active = db.Column(db.Boolean)
    access_level = db.Column(db.Integer)
    status = db.Column(db.Integer)
    
    def __init__(self, name, permission_level):
        self.name = name
        self.access_level = permission_level
        self.api_key = generate_api_token()

# Model to store notifications   
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String)
    dismissed = db.Column(db.Boolean)
    
    def __init__(self, body):
        self.body = body
