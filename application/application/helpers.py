from flask import redirect, session, render_template
from functools import wraps
import re

status = ["Preparing", "Casual meeting", "Sent resume", "1st interview", "2nd interview", "3rd interview",
          "4th interview", "5th interview", "6th interview", "Final interview", "Offer", "Technical test", "Rejected", "Accepted", "On hold"]

valid_characters = '^[a-zA-Z0-9_-]+$'

error_messages = {
    0: "may only use underscore, dash or alphanumeric characters",
    1: "must provide both username and password",
    2: "confirmation did not match password",
    3: "username is already used",
    4: "invalid username and/or password",
    5: "input length is not valid"
}

string_length = {
    "username": {"min": 3, "max": 20},
    "password": {"min": 3, "max": 30}
}


def check_characters(list):
    """
    https://www.geeksforgeeks.org/python-check-if-string-contain-only-defined-characters-using-regex/
    """
    for string in list:
        regex = re.compile(valid_characters)
        if bool(re.search(regex, string)) == False:
            return False
    return True


def check_length(string_length, pattern):
    return string_length >= pattern["min"] and string_length <= pattern["max"]


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def error(error):
    message = error_messages[error]
    return display_error(message)


def display_error(message, code=400):
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("error.html", top=code, bottom=escape(message)), code
