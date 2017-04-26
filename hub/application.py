from flask import Flask, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

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
# -- portal
#   -- GET permission level [0]
#   -- PUT request permission level update [0] [1]

# [0] = requires to be a registered device
# [1] = needs to be approved by user
# [2] = requires special permissions