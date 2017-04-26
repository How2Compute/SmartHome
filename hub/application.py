from flask import Flask, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# GUI
@app.route('/')
def index():
    return(render_template('index.html'))

# API