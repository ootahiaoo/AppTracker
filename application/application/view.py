from application import app, controller
from application.helpers import check_characters, is_rank_format, is_time_format, login_required, status, error, display_error, check_length, length_pattern, set_empty_response
from flask import Flask, redirect, render_template, request, session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


@app.route("/")
@login_required
def index():
    user = controller.get_user_by_id(session["user_id"])
    if not user:
        return error(6, 404)
    projects = controller.get_all_projects(session["user_id"])
    return render_template("index.html", name=user.username, projects=projects)


@app.route("/new_project", methods=["GET", "POST"])
@login_required
def new_project():
    if request.method == "GET":
        return render_template("new_project.html")

    project_name = set_empty_response("project-name")
    project_memo = set_empty_response("project-memo")

    if (check_length(project_name, length_pattern["project_name"])
            and check_length(project_memo, length_pattern["memo"])) == False:
        return error(5)

    created_on = datetime.now().strftime('%d-%m-%Y %H:%M')

    controller.create_project(
        session["user_id"], created_on, project_name, project_memo)

    return redirect("/")


@app.route("/edit_project_<project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    if request.method == "GET":
        project = controller.get_project(project_id)
        if not project:
            return error(6, 404)
        return render_template("edit_project.html", project=project)

    project_name = set_empty_response("project-name")
    starting_date = set_empty_response("starting-date")
    ending_date = set_empty_response("ending-date")
    project_memo = set_empty_response("project-memo")

    if (check_length(project_name, length_pattern["project_name"])
            and check_length(project_memo, length_pattern["memo"])) == False:
        return error(5)

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

    company_name = request.form.get("company-name")
    role = request.form.get("role")
    rank = request.form.get("application-rank")
    if not company_name or not role or not rank:
        return error(7)

    date = request.form.get("status-date")
    time = request.form.get("status-time")
    memo = set_empty_response("application-memo")
    application_status = request.form.get("default-status")
    if not application_status:
        application_status = set_empty_response("custom-status")

    if not date or not time:
        datetime = ""
    else:
        if is_time_format(time) == False:
            return error(8)
        datetime = date + " " + time

    if (check_length(company_name, length_pattern["company_name"])
        and check_length(role, length_pattern["role"])
        and check_length(memo, length_pattern["memo"])
        and check_length(application_status, length_pattern["stage"])
        and check_length(rank, length_pattern["rank"])
            and check_length(datetime, length_pattern["datetime"])) == False:
        return error(5)

    if is_rank_format(rank) == False:
        return error(10)

    company = controller.search_company(company_name)
    if not company:
        controller.create_company(company_name)
        company_id = controller.get_company_id(company_name)
    else:
        company_id = company[0].id

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

    role = request.form.get("role-name")
    rank = request.form.get("application-rank")
    if not role or not rank:
        return error(9)
    memo = set_empty_response("application-memo")

    if (check_length(role, length_pattern["role"])
        and check_length(rank, length_pattern["rank"])
            and check_length(memo, length_pattern["memo"])) == False:
        return error(5)

    if is_rank_format(rank) == False:
        return error(10)

    controller.edit_application(application_id, role, rank, memo)
    return application_details(application_id)


@app.route("/new_stage_<application_id>", methods=["GET", "POST"])
@login_required
def add_stage(application_id):
    if request.method == "GET":
        return render_template("new_stage.html", application_id=application_id, stages=status)

    date = request.form.get("stage-date")
    time = request.form.get("stage-time")
    stage_memo = set_empty_response("stage-memo")
    type = request.form.get("default-status")
    if not type:
        type = set_empty_response("custom-status")

    if not date or not time:
        datetime = ""
    else:
        if is_time_format(time) == False:
            return error(8)
        datetime = date + " " + time

    if (check_length(datetime, length_pattern["datetime"])
        and check_length(stage_memo, length_pattern["memo"])
            and check_length(type, length_pattern["stage"])) == False:
        return error(5)

    controller.create_stage(application_id, type, datetime, stage_memo)

    return application_details(application_id)


@app.route("/edit_stage_<stage_id>", methods=["GET", "POST"])
@login_required
def edit_stage(stage_id):
    stage = controller.get_stage(stage_id)
    if request.method == "GET":
        return render_template("edit_stage.html", stage=stage)

    date = request.form.get("stage-date")
    time = request.form.get("stage-time")
    stage_memo = set_empty_response("stage_memo")
    type = request.form.get("default-status")
    if not type:
        type = set_empty_response("custom-status")
    
    if not date or not time:
        datetime = ""
    else:
        if is_time_format(time) == False:
            return error(8)
        datetime = date + " " + time

    if (check_length(datetime, length_pattern["datetime"])
        and check_length(stage_memo, length_pattern["memo"])
            and check_length(type, length_pattern["stage"])) == False:
        return error(5)
    
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

    if (check_length(username, length_pattern["username"])
            and check_length(password, length_pattern["password"])) == False:
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

    if (check_length(username, length_pattern["username"])
        and check_length(password, length_pattern["password"])
            and check_length(confirmation, length_pattern["password"])) == False:
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


@app.route("/check_existing_<company_name>", methods=["POST"])
def check_existing_company(company_name):
    """ Used by Javascript when creating new application """
    return controller.search_company_js(company_name)


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
