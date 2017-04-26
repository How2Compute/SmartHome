from flask import Flask, jsonify, render_template, session, abort, request
from Models import db, Device, Notification, User, Preference
from helpers import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///hub.db"
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)

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
#   -- POST approve [2]
#   -- POST unapprove [2]

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
# -- devices
#   -- List Devices  
@app.route('/api/0.1/devices', methods=['GET'])
@permission_required(1)
def list_all_devices():
    result = Device.query.all()
    
    # Create an empty array to store the devices
    devices = []
    
    # Filter out the statuts/device api key (due to security/unnecciserities) + id -> uri
    for device in result:
        # Copy the *required* parameters over to a new variable
        _device = {
            'id': device.id,
            'name': device.name,
            'permission_level': device.access_level,
            'active': device.active
        }
        
        # Add it to the devices list
        devices.append(_device)
    
    # Return all of the devices (without their api key and status)
    return jsonify(devices)

# -- devices
#   -- device status
@app.route('/api/0.1/devices/<int:id>', methods=['GET'])
@permission_required(0)
def get_status_unique(id):
    device = Device.query.filter(Device.id == id).first()
    # "dirty" way to check if this is the clients it's own device
    if device.api_key == request.json.get('api_key'):
        return jsonify({ "status": device.status })
    else:
        @permission_required(1)
        def other_status():
            return jsonify({ "status": device.status })
        return other_status()

# -- devices
#   -- new status
@app.route('/api/0.1/devices/<int:id>', methods=['PUT'])
@permission_required(0)
def update_status(id):
    if not request.json or 'api_key' not in request.json or 'status' not in request.json:
        return abort(400)
    # "dirty" way to check if this is the clients it's own device
    device = Device.query.filter(Device.id == id).first()
    if device.api_key == request.json.get('api_key'):
        # Update the device it's status
        device.status = request.json.get('status')
        db.session.commit()
        
        return jsonify({ "success": "true" })
    else:
        @permission_required(1)
        def other_status():
            # Update the device it's status
            device.status = request.json.get('status')
            db.session.commit()
            return jsonify({ "success": "true" })
        return other_status()
        
# -- Device
#   -- Remove Device
# TODO evaluate deactivate vs destroy/delete from db
@app.route('/api/0.1/devices/<int:id>', methods=['DELETE'])
@permission_required(0)
def remove_device(id):
    # Verify the request contains an API key
    if not request.json or 'api_key' not in request.json:
        return abort(400)
        
    # "dirty" way to check if this is the clients it's own device
    device = Device.query.filter(Device.id == id).first()
    if device.api_key == request.json.get('api_key'):
        # Delete the device from the database
        db.session.delete(device)
        db.session.commit()
        return jsonify({ "success": "true" })
    else:
        @permission_required(1)
        def remove_other():
            # Delete the device from the database
            db.session.delete(device)
            db.session.commit()
            return jsonify({ "success": "true" })
        return remove_other()
        
# -- users
#   -- list all users
@app.route('/api/0.1/users', methods=['GET', 'DELETE'])
#@permission_required(1)
def get_users():
    users = User.query.all()
    preferences = users[0].preferences
    users_len = len(users)
    preferences_len = len(preferences)
    print(len(users))
    return jsonify({"len_users": users_len, "len_preferences": preferences_len})