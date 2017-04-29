import string
import random

from functools import wraps
# Include database models
from Models import db, Device
from flask import session, abort, request, url_for, redirect

# Generate an api key prefixed with api_ (adapted from http://stackoverflow.com/a/23728630)
def generate_api_token():
    token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(46))
    return 'api_' + token

"""
def permission_required(f, n):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
"""
# Take in a parameter (the permission level) based on http://stackoverflow.com/a/30853548
def permission_required(permission):
    def decorator (f):
            
        @wraps(f)
        def decorated_view(*args, **kwargs):
            # Did the client provide an API key?
            if not request.json or not 'api_key' in request.json:
                return abort(400)
            
            client = Device.query.filter(Device.api_key == request.json.get('api_key')).first()
            
            # Invalid API key!
            if not client:
                # Notify the user? Possible intrusion attempt? TODO
                return abort(403)
            # Check if the device is active
            if not client.active:
                return abort(403)
            # Check if the device has the correct permission TODO make this actually check a uint8/uint16!
            if not (client.access_level >= permission):
                return abort(403)
            
            return f(*args, **kwargs)
        return decorated_view
    return decorator

"""
Get the permission level of a preference for an API token.
0: No Permission
1: Read Permission (access_level >= access_required OR is the tokens' own preference)
2: Read/Write Permission (accesslevel > access required OR is the tokens' own preference)
"""
def get_preference_perms(api_token, preference):
    
    result = Device.query.filter(Device.api_key == api_token).first()
    # Could not find API key
    if not result:
        return 0
        
    # Does this device own it?
    if preference.device_id == result.id or result.access_level > preference.access_required:
        return 2
    # Same access level?
    elif result.access_level == preference.access_required:
        return 1
    # None of the above true? No permisions it is!
    else:
        return 0

# Returns the users URI (based upon ID)
def user_IDtoURI(id):
    # TODO make the api string get_user instead of get_users
    return '{}/{}'.format(url_for('get_user', _external=True, id=id))

"""
Ensures user is logged in.
(and redirects the user to the login page if they are not)
"""
def logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if the sessions ID was not set, assume the user was not logged in
        if not session.get('id'):
            return redirect(url_for('dash_login'))
        return f(*args, **kwargs)
    return decorated_function