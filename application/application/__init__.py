import os
from flask import Flask
from flask_session import Session
from tempfile import mkdtemp

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

from application import view
from application import helpers
from application import model
from application import controller

if __name__ == "__main__":
    app.run()