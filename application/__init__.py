from flask import Flask
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

from application import controller
from application import model
from application import helpers
from application import view

@app.context_processor
def utility_processor():
    """
    Custom filter for Jinja:
    The project creation date stores the time too,
    but only displays the date on the homepage
    https://stackoverflow.com/questions/6036082/call-a-python-function-from-jinja2/22966127#22966127
    """
    def simplify_date(datetime_string):
        return datetime.strptime(datetime_string, "%d-%m-%Y %H:%M").date()
    return dict(simplify_date=simplify_date)


if __name__ == "__main__":
    app.run()
