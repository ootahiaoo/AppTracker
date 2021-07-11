from application import app, controller
from application.helpers import check_characters, login_required, status, error, display_error, check_length, string_length
from flask import Flask, redirect, render_template, request, session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


@app.route("/")
@login_required
def index():
    user = controller.get_user_by_id(session["user_id"])
    if not user:
        return "error"

    projects = controller.get_all_projects(session["user_id"])

    return render_template("index.html", name=user.username, projects=projects)


@app.route("/new_project", methods=["GET", "POST"])
@login_required
def new_project():
    if request.method == "GET":
        return render_template("new_project.html")

    project_name = request.form.get("project_name")
    project_memo = request.form.get("project_memo")

    created_on = datetime.now().strftime('%d-%m-%Y %H:%M')

    controller.create_project(
        session["user_id"], created_on, project_name, project_memo)

    return redirect("/")


@app.route("/edit_project_<project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    if request.method == "GET":
        project = controller.get_project(project_id)
        return render_template("edit_project.html", project=project)
    project_name = request.form.get("project_name")
    starting_date = request.form.get("starting_date")
    ending_date = request.form.get("ending_date")
    project_memo = request.form.get("project_memo")

    controller.edit_project(project_id, project_name,
                            starting_date, ending_date, project_memo)
    return redirect("/")


@app.route("/dashboard_<project_id>", methods=["GET", "POST"])
@login_required
def dashboard(project_id):
    # Merge requests?
    project = controller.get_project(project_id)
    applications = controller.get_all_applications(project_id)
    return render_template("dashboard.html", project=project, applications=applications)


@app.route("/new_application_<project_id>", methods=["GET", "POST"])
@login_required
def new_application(project_id):
    if request.method == "GET":
        return render_template("new_application.html", project_id=project_id, stages=status)

    # TODO: check input
    company_name = request.form.get("company_name")
    role = request.form.get("role")
    memo = request.form.get("application_memo")
    application_status = request.form.get("application_status")
    if not application_status:
        application_status = request.form.get("custom_status")

    date = request.form.get("status_date")
    time = request.form.get("status_time")
    datetime = date + " " + time

    rank = request.form.get("application_rank")
    if not company_name or not role:
        return "must provide a company name and a role"

    # TODO: check if company already exists
    # if yes, use that id
    controller.create_company(company_name)
    company_id = controller.get_company_id(company_name)

    controller.create_application(
        project_id, company_id, role, memo, rank, application_status, datetime)

    return dashboard(project_id)


@app.route("/application_details_<application_id>", methods=["GET", "POST"])
@login_required
def application_details(application_id):
    # TODO: merge requests?
    application = controller.get_simple_application(application_id)
    stages = controller.get_process(application_id)
    return render_template("application_details.html", application_id=application_id, application=application, stages=stages)


@app.route("/edit_application_<application_id>", methods=["GET", "POST"])
@login_required
def edit_application(application_id):
    application = controller.get_application(application_id)
    if request.method == "GET":
        return render_template("edit_application.html", application=application)

    role = request.form.get("role_name")
    rank = request.form.get("application_rank")
    memo = request.form.get("application_memo")

    controller.edit_application(application_id, role, rank, memo)
    return application_details(application_id)


@app.route("/new_stage_<application_id>", methods=["GET", "POST"])
@login_required
def add_stage(application_id):
    if request.method == "GET":
        return render_template("new_stage.html", application_id=application_id, stages=status)
    type = request.form.get("stage_status")
    if not type:
        type = request.form.get("custom_status")
    date = request.form.get("stage_date")
    time = request.form.get("stage_time")
    if not date or not time:
        datetime = ""
    else:
        datetime = date + " " + time
    stage_memo = request.form.get("stage_memo")
    controller.create_stage(application_id, type, datetime, stage_memo)

    return application_details(application_id)


@app.route("/edit_stage_<stage_id>", methods=["GET", "POST"])
@login_required
def edit_stage(stage_id):
    stage = controller.get_stage(stage_id)
    if request.method == "GET":
        return render_template("edit_stage.html", stage=stage)

    type = request.form.get("stage_status")
    if not type:
        type = request.form.get("custom_status")
    date = request.form.get("stage_date")
    time = request.form.get("stage_time")
    if not date or not time:
        datetime = ""
    else:
        datetime = date + " " + time
    stage_memo = request.form.get("stage_memo")
    if not stage_memo:
        stage_memo = ""
    controller.edit_stage(stage_id, type, datetime, stage_memo)

    return application_details(stage.application_id)


@app.route("/company_<company_id>", methods=["GET", "POST"])
@login_required
def company_details(company_id):
    company = controller.get_company(company_id)
    history = controller.get_company_history(company_id)
    return render_template("company_details.html", company=company, history=history)


@app.route("/search", methods=["POST"])
@login_required
def search():
    keyword = request.form.get("q")
    results = controller.search_company(keyword)
    return render_template("search_result.html", keyword=keyword, results=results)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username-login")
    password = request.form.get("password-login")

    if not username or not password:
        return error(1)
    if check_characters([username, password]) == False:
        return error(0)

    if (check_length(len(username), string_length["username"]) == False
            or check_length(len(password), string_length["password"]) == False):
        return error(5)

    user = controller.get_user_by_username(username)
    if not user or not check_password_hash(user.hash, password):
        return error(4)

    session["user_id"] = user.id
    return redirect("/")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username-register")
    password = request.form.get("password-register")
    confirmation = request.form.get("confirmation-register")

    if not username or not password or not confirmation:
        return error(1)

    if check_characters([username, password, confirmation]) == False:
        return error(0)

    if (check_length(len(username), string_length["username"]) == False
        or check_length(len(password), string_length["password"]) == False
            or check_length(len(confirmation), string_length["password"]) == False):
        return error(5)

    if password != confirmation:
        return error(2)

    user = controller.get_user_by_username(username)
    if user != None:
        return error(3)

    controller.register_user(username, generate_password_hash(password))

    user = controller.get_user_by_username(username)
    session["user_id"] = user.id

    return redirect("/")


@app.route("/check_username_<username>", methods=["POST"])
def check_username_availability(username):
    """ Used by Javascript on the login screen """
    value = controller.get_user_by_username(username)
    if value != None:
        return "Not available"
    return "Available"


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return display_error(e.name, e.code)


for code in default_exceptions:
    """ Listen for errors """
    app.errorhandler(code)(errorhandler)
