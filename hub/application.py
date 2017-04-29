from flask import Flask, jsonify, render_template, session, abort, request, url_for, send_from_directory, flash, session, redirect
from flask.ext.session import Session
from Models import db, Device, Notification, User, Preference
from helpers import *
from tempfile import mkdtemp
from passlib.hash import argon2

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///hub.db"
app.config['SQLALCHEMY_ECHO'] = True

# configure session to use filesystem (instead of signed cookies) (copied from pset7 cs50 code)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db.init_app(app)

# Allow flask to serve up static files without nginx
@app.route('/vendors/<path:path>')
def send_vendors(path):
    return send_from_directory('static/vendors', path)
@app.route('/build/<path:path>')
def send_build(path):
    return send_from_directory('static/build', path)
@app.route('/images/<path:path>')
def send_production(path):
    return send_from_directory('static/production/images', path)
@app.route('/scripts/<path:path>')
def send_script(path):
    return send_from_directory('static/scripts', path)
    
# GUI
@app.route('/')
@logged_in
def dash_index():
    notifications = Notification.query.all()
    return render_template('index.html', username=session['username'], notifications = notifications)

@app.route('/devices')
@logged_in
def dash_list_livices():
    results = Device.query.all()
    
    devices = []
    
    for device in results:
        _device = {
            'id': device.id,
            'name': device.name,
            'permission_level': device.access_level,
            'active': device.active
        }
        devices.append(_device)
        
    notifications = Notification.query.all()
    
    return render_template('devices.html', devices=devices, username=session['username'], notifications = notifications)

@app.route('/login', methods=['GET', 'POST'])
def dash_login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        
        if not request.form.get("username") or not request.form.get("password"):
            flash("You forgot to enter your username and/or password!")
            return redirect(url_for('dash_login'))

        user = User.query.filter(User.username == request.form.get('username')).first()

        if not user:
            flash("Incorrect username! and/or password!")
            return redirect(url_for('dash_login'))
        # Check Credentials
        if argon2.verify(request.form.get('password'), user.password):
            # login success
            session['id'] = user.id
            session['username'] = user.username
            session['access_level'] = user.access_level
            return redirect(url_for('portal'))
        else:
            flash("Incorrect username and/or password!")
            return redirect(url_for('dash_login'))
    else:
        return abort(400)

# Log the user out (ensure the user is logged in, as logging out a logged out user makes no sense)
@app.route('/logout', methods=['GET', 'POST'])
@logged_in
def dash_logout():
    # Clear the session, effectively logging the user out
    session.clear()
    # Redirect them to the login page showing them a successfully logged out page
    flash("Successfully logged out!")
    return redirect(url_for('dash_login'))

@app.route('/home-portal')
@logged_in
def portal():
    devices = Device.query.all()
    notifications = Notification.query.all()
    return render_template('portal.html', devices=devices, username=session['username'], notifications = notifications)

@app.route('/update/<int:device_id>')
@logged_in
def dash_update_device(device_id):
    device = Device.query.filter(Device.id == device_id).first()
    
    if not device:
        return abort(404)
    
    # manually format these to filter out id and to allow preferences to be keys too    
    properties = [{
        "key": "name",
        "value": device.name
    },
    {
        "key": "access_level",
        "value": device.access_level
    },
    {
        "key": "api_key",
        "value": device.api_key
    },
    {
        "key": "active",
        "value": device.active
    },
    {
        "key": "status",
        "value": device.status
    }]
    
    # Retrieve the users' preferences related to the specified device
    preferences = Preference.query.filter_by(device_id=device_id, user_id=session.get('id'))
    
    # Copy all the preferences their keys/values
    for preference in preferences:
        properties.append({
            "key": preference.key,
            "value": preference.value
        })
    
    notifications = Notification.query.all()
    return render_template('updateDevice.html', device=device, properties=properties, username=session['username'], notifications = notifications)
    
    return abort(403)
    
@app.route('/update/<int:device_id>/<key>/<value>', methods=['PUT'])
@logged_in
def updateKey(device_id, key, value):
    # Retrieve the database record for this user #, device # and key
    preference = Preference.query.filter_by(device_id=device_id, key=key, user_id=session.get('id')).first()
    
    # Was the preference found?
    if not preference:
        # If it's not a preference, is it a device key instead?
        device = Device.query.filter_by(id=device_id).first()
        # Did we hit a device?
        if not device:
            return abort(404)
        if key == 'name':
            device.name = value
        elif key == 'api_key':
            # Ensure api key starts with api_
            if value[:4] != "api_":
                return abort(400)
            
            device.api_key = value
        elif key == 'access_level':
            device.access_level = value
        elif key == 'active':
            device.active = value
        elif key == 'status':
            device.status = value
        # If not it could not find the key
        else:
            return abort(404)
        
        # Commit the device change (here to avoid duplicate code) and return success
        db.session.commit()
        return jsonify({"success": "true"})
    
    else:
        # Alter value, save and return success
        preference.value = value
        db.session.commit()
        return jsonify({"success": "true"})

@app.route('/delete/<int:device_id>', methods=['POST'])
@logged_in
def dash_delete_device(device_id):
    # 2 is the minimum required access level to delete a device!
    if session['access_level'] < 2:
       return abort(403)
    
    device = Device.query.filter(Device.id == device_id).first()
    
    # Was the device found?
    if not device:
        return abort(404)
    
    # Remove the device from the database
    db.session.delete(device)
    db.session.commit()
    
    # Return a json success response
    return jsonify({'success': 'true'})
    
@app.route('/approve', methods=['GET', 'POST'])
@logged_in
def dash_approve():
    if request.method == 'GET':
        # Get the devices that are not active
        devices = Device.query.filter(Device.active != True)
        notifications = Notification.query.all()
        # Render list of unapproved devices with accept/deny button that posts this URL (with AJAX)
        return render_template('approve.html', devices=devices, username=session['username'], notifications = notifications)
    elif request.method == 'POST':
        if not request.json or 'id' not in request.json or 'approve' not in request.json:
            # We didn't have all the info, so couldn't understand the request!
            return abort(400)
        else:
            # Get the requests device id and fall back on -1 if it could somehow not get it
            device = Device.query.filter_by(id=request.json.get('id', -1))
            # If the device was not found return a 404 (not found)
            if not device:
                return abort(404)
        
            # Delete the device if it was not approved (fall back on True AKA do not delete if it somehow was invalid)
            if not request.json.get('approve', True):
                # Get the requests device id and fall back on -1 if it could somehow not get it
                device.delete()
                db.session.commit()
                # Return success
                return jsonify({"success": "true"})
            else:
                # Set the device to active
                device.first().active = True;
                db.session.commit()
                # Return failiure
                return jsonify({"success": "true"})
            
    else:
        # Method not supported!
        return abort(405)

# If the user tries to access the api, redirect them to the index page
@app.route('/api/', methods=['GET'])
def api_ui():
    return redirect(url_for('dash_index'))

# API
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
#   -- GET preferences [1] (clients') [2+] (depending on preference)
#   -- PUT preference [1] (clients') [2+] (depending on preference)
#   -- DELETE preference [1] (clients') [2+] (depending on preference)
# -- portal
#   -- GET is device active [0] (self) [1] (other)
#   -- GET permission level [0]
#   -- PUT request permission level update [0] [1] - DEPRICATED (can only be done through control panel) (due to security issues)
#   -- POST (un)approve [2]

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
        print("No json!")
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
    
    # Adds notification about the fact a new device has been added
    notification = Notification(-120, "Devices", "New device needs your approval!", "A new device just tried to register! Please approve it in your devices page.", url_for('dash_approve'))
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
@app.route('/api/0.1/users', methods=['GET'])
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
#   -- get preferences
@app.route('/api/0.1/users/<int:id>/preferences', methods=['GET'])
@permission_required(1)
def get_preferences(id):
    if not request.json or 'api_key' not in request.json:
        return abort(400)
    
    # List all this users' preferences
    result = User.query.filter(User.id == id).first()
    
    if not result:
        return abort(404)
    else:
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
    
    # return the preferences array back to the user
    return jsonify(preferences)

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
@app.route('/api/0.1/portal/approved', methods=['GET'])
@permission_required(0)
def is_active_self():
    if not request.json or 'api_key' not in request.json:
        return abort(400)
    
    # Get the device of the api key
    device = Device.query.filter(Device.api_key == request.json.get('api_key')).first()
    # Was the device found?
    if not device:
        return abort(404)
        
    # Use the "real" function with the api_keys' device id
    return is_active(device.id)
    
@app.route('/api/0.1/portal/approved/<int:device_id>', methods=['GET'])
@permission_required(0)
def is_active(device_id):
    if not request.json or 'api_key' not in request.json:
        return abort(400)
    device = Device.query.filter(Device.id == device_id).first()
    if not device:
        return abort(404)
    
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

# -- portal
#   -- approve/disapprove device
@app.route('/api/0.1/portal/approved/<int:device_id>', methods=['POST'])
@permission_required(1)
def approve_device(device_id):
    if not request.json or 'approve' not in request.json:
        return abort(400)
    
    device = Device.query.filter(Device.id == device_id).first()
    
    if not device:
        return abort(404)
    
    # Set the device to approved if true was passed in in json, and otherwise set it to false
    device.active = request.json.get('approve') == 'true'
    # Save this change to the database
    db.session.commit()
    
    return jsonify({ "success": "true" })

@app.route('/api/0.1/portal/permissions', methods=['GET'])
@permission_required(0)
def get_permissions_self():
    if not request.json or 'api_key' not in request.json:
        return abort(400)
    
    # Get the device of the api key
    device = Device.query.filter(Device.api_key == request.json.get('api_key')).first()
    # Was the device found?
    if not device:
        return abort(404)
        
    # Use the "real" function with the api_keys' device id
    return get_permissions(device.id)
    
@app.route('/api/0.1/portal/permissions/<int:device_id>', methods=['GET'])
@permission_required(0)
def get_permissions(device_id):
    if not request.json or 'api_key' not in request.json:
        return abort(400)
    
    device = Device.query.filter(Device.id == device_id).first()
    if not device:
        return abort(404)
    
    # Allow byepassing of permission check if it's the api keys' device
    if device.api_key == request.json.get('api_key'):
        return jsonify({ 'level': device.access_level })
    
    # In a function which assures correct permissions
    @permission_required(1)
    def is_active_other():
        return jsonify({ 'level': device.access_level })
    return is_active_other()

