from flask import Flask, jsonify, render_template, session, abort
from flask_sqlalchemy import SQLAlchemy
from helpers import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///hub.db"
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Device(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text)
    api_key = db.Column(db.Text)
    active = db.Column(db.Boolean)
    permission_level = db.Column(db.Integer)
    
    def __init__(name, permission_level):
        self.name = name
        self.permission_level = permission_level
        self.api_key = generate_api_token()

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
    # Was the name provided?
    if 'name' not in request.json or type(request.json.get('name') != string):
        abort(400)
    # Was the permission level provided?    
    elif 'permission_level' not in request.json or type(request.json.get('permission_level') != integer):
        abort(400)
    
    # Insert into devices table as pending
    device = Device()
    # Notify User
    # Return successfully made request (but not yet approved). Also send API keys etc
    return jsonify({
        "status": "Unapproved",
        "credentials": #TODO
    })