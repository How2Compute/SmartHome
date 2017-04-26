from flask import Flask, jsonify, render_template, session, abort, request, url_for
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
#   -- PUT user data [2] - DEPRICATED (can only be done through control panel) (semi-replaced by preference functions)
#   -- POST user data [2] - DEPRICATED (can only be done through control panel) (semi-replaced by preference functions)
#   -- POST notify user [2]
#   -- POST preference [1]
#   -- PUT preference [1] (clients') [2+] (depending on preference)
#   -- DELETE preference [1] (clients') [2+] (depending on preference)
# -- portal
#   -- GET is device active [1]
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
    # Select all of the users 
    result = User.query.with_entities(User.id, User.username, User.access_level)
    users = []
    for user in result:
        _user = {
            'URI': user_IDtoURI(user.id),
            'username': user.username,
            'access_level': user.access_level
        }
        users.append(_user)
    
    return jsonify(users)
    
# -- users
#   -- get user data
@app.route('/api/0.1/users/<int:id>', methods=['GET'])
@permission_required(1)
def get_user(id):
    result = User.query.filter(User.id == id).first()
    
    # Did it successfully retrieve the user?
    if not result:
        return abort(404)
    
    # Make the preferences serializable
    preferences = []
    for preference in result.preferences:
        # Ensure that the application has permission to access the preference
        if get_preference_perms(request.json.get('api_key'), preference) > 0:
            # Get the relevant fields from the preference
            _preference = {
                'key': preference.key,
                'value': preference.value
            }
            # Add it to the preferences (the client has access to) list
            preferences.append(_preference)
        
    # Filter out some things for security (password hash & analytics token) & make it JSON serializable
    user = {
        'id': result.id,
        'username': result.username,
        'last_login': result.last_login,
        'create_date': result.create_date,
        'access_level': result.access_level,
        'preferences': preferences
    }
    # Return the user in json
    return jsonify(user)

# -- Users
#   -- add preference
@app.route('/api/0.1/users/<int:id>/preferences', methods=['POST'])
@permission_required(1)
def add_preference(id):
    if not request.json or 'key' not in request.json or 'value' not in request.json:
        return abort(400)
    
    result = User.query.filter(id == id).first()
    
    device_id_result = Device.query.filter(Device.api_key == request.json.get('api_key')).first()
    if not device_id_result:
        return abort(403)
    device_id = device_id_result.id
    
    # Was there actually a user by the specified id?
    if not result:
        return abort(404)
    
    # Check if the key is already in the database
    # TODO make this go into 1 query and get it's length?
    for preference in result.preferences:
        if preference.key == request.json.get('key'):
            return abort(409) # Return HTTP conflict error
    
    # Create a preference object with the json data, using permissionlevel 0 for access_requirements if none are provided
    preference = Preference(id, device_id, request.json.get('key'), request.json.get('value'), request.json.get('access_required', 0))
    # Insert the preference into the database
    db.session.add(preference)
    db.session.commit()
    
    return jsonify({
        "status": "success"
    })

# -- users
#   -- update value of a given key
@app.route('/api/0.1/users/<int:user_id>/preferences/<preference_key>', methods=['PUT'])
@permission_required(1)
def update_preference(user_id, preference_key):
    if not request.json or 'value' not in request.json:# or type(request.json.get('value')) != unicode:
        return abort(400)
    
    preference = Preference.query.filter_by(user_id=user_id, key=preference_key).first()
    
    if not preference:
        return abort(404)
    
    # Get the permission level and if it's not 2, return a forbiden error
    permission_level = get_preference_perms(request.json.get('api_key'), preference)
    if permission_level != 2:
        return abort(403)
    
    # Set the preference it's value and send it to the database
    preference.value = request.json.get('value', preference.value)
    db.session.commit()
    
    return jsonify({ "success": "true" })

# -- users
#   -- delete preference
@app.route('/api/0.1/users/<int:user_id>/preferences/<preference_key>', methods=['DELETE'])
@permission_required(1)
def remove_preference(user_id, preference_key):
    preference = Preference.query.filter_by(user_id=user_id, key=preference_key).first()
    
    # Was the preference found?
    if not preference:
        return abort(404)
    
    # Get the permission level and if it's not 2, return a forbiden error
    permission_level = get_preference_perms(request.json.get('api_key'), preference)
    if permission_level != 2:
        return abort(403)
    else:
        # Remove the preference from existence
        db.session.delete(preference)
        db.session.commit()
        
        return jsonify({ "success": "true"})
        
# -- portal
#   -- is this an active device
@app.route('/api/0.1/portal/approved/<int:device_id>', methods=['GET'])
@permission_required(0)
def is_active(device_id):
    if not request.json or 'api_key' not in request.json:
        return abort(400)
    device = Device.query.filter(Device.id == device_id).first()
    if device.api_key == request.json.get('api_key'):
        return jsonify({
            'status': 'active' if device.active else 'inactive'
        })
    # In a function which assures correct permissions
    @permission_required(1)
    def is_active_other():
        return jsonify({
            'status': 'active' if device.active else 'inactive'
        })
    return is_active_other()