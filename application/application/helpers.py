from flask import redirect, session
from functools import wraps

status = ["Preparing", "Casual meeting", "Sent resume", "1st interview", "2nd interview", "3rd interview",
          "4th interview", "5th interview", "6th interview", "Final interview", "Offer", "Technical test", "Rejected", "Accepted", "On hold"]


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