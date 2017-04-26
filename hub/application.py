from flask import Flask, jsonify, render_template, session, abort, request
from flask_sqlalchemy import SQLAlchemy
from helpers import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///hub.db"
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

# Model to store information about devices
class Device(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text)
    api_key = db.Column(db.Text)
    active = db.Column(db.Boolean)
    access_level = db.Column(db.Integer)
    
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

# GUI
@app.route('/')
def index():
    return render_template('index.html')

# API
@app.route('/api/', methods=['GET'])
def api_ui():
    # The user tried to access the api portal, show them dev getting started instructions (TODO)
    return render_template('index.html')

# /api
# -- devices
#   -- POST register device [1]
#   -- GET devices [2]
#   -- GET (own) device status [0]
#   -- PUT new status
#   -- DELETE remove device [0] (for self) [2] (for other)
# -- users
#   -- GET list of users [2]
#   -- GET user data [2]
#   -- PUT user data [2]
#   -- POST user data [2]
#   -- POST notify user [2]
# -- portal
#   -- GET is registered
#   -- GET permission level [0]
#   -- PUT request permission level update [0] [1]

# [0] = requires to be a registered device
# [1] = needs to be approved by user
# [2] = requires special permissions

# API
# -- devices
#   -- Register Device
@app.route('/api/0.1/devices', methods=['POST'])
def register():
    # Was json entered?
    if not request.json:
        abort(400)
    # Was the name provided?
    elif 'name' not in request.json:# or type(request.json.get('name')) != string:
        abort(400)
    # Was the permission level provided?    
    elif 'permission_level' not in request.json:# or type(request.json.get('permission_level') != integer):
        abort(400)
    
    # Insert into devices table as pending
    device = Device(request.json.get('name'), request.json.get('permission_level'))
    db.session.add(device)
    db.session.commit()
    # Notify User TODO make this also hold a title, call to action URL/URI etc
    notification = Notification("A new device just tried to register! Please approve it in your devices page.")
    db.session.add(notification)
    db.session.commit();
    
    # Return successfully made request (but not yet approved). Also send API keys etc
    return jsonify({
        "status": "Unapproved",
        "id": device.id,
        "api_key": device.api_key
    })