from flask import redirect, session, render_template, request
from functools import wraps
import time
import re

status = ["Preparing", "Casual meeting", "Sent resume", "1st interview",
          "2nd interview", "3rd interview", "4th interview", "5th interview", "6th interview", "Final interview", "Offer", "Technical test", "Rejected", "Accepted", "On hold"]

error_messages = {
    0: "may only use underscore, dash or alphanumeric characters",
    1: "must provide both username and password",
    2: "confirmation did not match password",
    3: "username is already used",
    4: "invalid username and/or password",
    5: "input length is not valid",
    6: "not found",
    7: "must provide a company name, a role and a rank",
    8: "time format is not valid",
    9: "must provide a role and a rank",
    10: "rank format is not valid"
}

length_pattern = {
    "username": {"min": 3, "max": 20},
    "password": {"min": 3, "max": 30},
    "project_name": {"min": 0, "max": 50},
    "datetime": {"min": 0, "max": 16},
    "memo": {"min": 0, "max": 300},
    "role": {"min": 1, "max": 50},
    "rank": {"min": 1, "max": 3},
    "company_name": {"min": 1, "max": 50},
    "stage": {"min": 1, "max": 50}
}


def check_characters(list):
    """
    https://www.geeksforgeeks.org/python-check-if-string-contain-only-defined-characters-using-regex/
    """
    for string in list:
        regex = re.compile('^[a-zA-Z0-9_-]+$')
        if bool(re.search(regex, string)) == False:
            return False
    return True


def is_time_format(string):
    """
    https://stackoverflow.com/a/1322532/
    """
    time_pattern = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$')
    return bool(time_pattern.match(string))


def is_rank_format(string):
    if string.isdigit():
        return int(string) <= 100
    return False


def check_length(string, pattern):
    string_length = len(string)
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


def error(error, code=400):
    message = error_messages[error]
    return display_error(message, code)


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


def set_empty_response(request_name):
    """
    Handle the arguments that can be left empty on purpose
    """
    response = request.form.get(request_name)
    if not response:
        response = ""
    return response
