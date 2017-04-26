import string
import random

from functools import wraps
# Include database models
from Models import db, Device
from flask import abort, request

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
            # Check if the user has the correct permission TODO make this actually check a uint8/uint16!
            if client.access_level != 1:
                return abort(403)
            
            return f(*args, **kwargs)
        return decorated_view
    return decorator
