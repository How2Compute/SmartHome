import string
import random

# Generate an api key prefixed with api_ (adapted from http://stackoverflow.com/a/23728630)
def generate_api_token():
    token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(46))
    return 'api_' + token
