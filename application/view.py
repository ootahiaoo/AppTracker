from application import app
from application import controller
from application.helpers import is_valid_characters, is_rank_format,\
    is_time_format, login_required, STATUS_LIST, error, display_error, \
    is_correct_length, LENGTH_PATTERN, set_empty_response
from flask import Flask, redirect, render_template, request, session
from werkzeug.exceptions import default_exceptions, HTTPException, \
    InternalServerError
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

    if not (is_correct_length(project_name, LENGTH_PATTERN["project_name"])
            and is_correct_length(project_memo, LENGTH_PATTERN["memo"])):
        return error(5)

    format = "%Y-%m-%d %H:%M"
    created_on = datetime.now().strftime(format)

    last_project_date = controller.get_last_project_datetime(
        session["user_id"])
    if last_project_date != "":
        difference = datetime.strptime(last_project_date, format) \
            - datetime.strptime(created_on, format)
        if (difference.seconds < 60000):
            return error(12, 405)

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

    if not (is_correct_length(project_name, LENGTH_PATTERN["project_name"])
            and is_correct_length(project_memo, LENGTH_PATTERN["memo"])):
        return error(5)

    controller.edit_project(
        project_id, project_name, starting_date, ending_date, project_memo)
    return redirect("/")


@app.route("/dashboard_<project_id>", methods=["GET", "POST"])
@login_required
def dashboard(project_id):
    project = controller.get_project(project_id)
    applications = controller.get_all_applications(project_id)
    return render_template("dashboard.html",
                           project=project,
                           applications=applications)


@app.route("/new_application_<project_id>", methods=["GET", "POST"])
@login_required
def new_application(project_id):
    if request.method == "GET":
        return render_template("new_application.html",
                               project_id=project_id,
                               stages=STATUS_LIST)

    company_name = request.form.get("company-name")
    role = request.form.get("role")
    rank = request.form.get("application-rank")
    if not company_name or not role or not rank:
        return error(7)

    date = request.form.get("status-date")
    time = request.form.get("status-time")
    memo = set_empty_response("application-memo")

    # Default status takes priority
    default_status = request.form.get("default-status")
    custom_status = request.form.get("custom-status")
    if not default_status and not custom_status:
        return error(13)
    application_status = default_status
    if not default_status:
        application_status = custom_status

    if not date and not time:
        datetime = ""
    elif not date or not time:
        return error(11)
    else:
        if not is_time_format(time):
            return error(8)
        datetime = date + " " + time

    if not (is_correct_length(company_name, LENGTH_PATTERN["company_name"])
            and is_correct_length(role, LENGTH_PATTERN["role"])
            and is_correct_length(memo, LENGTH_PATTERN["memo"])
            and is_correct_length(application_status, LENGTH_PATTERN["stage"])
            and is_correct_length(rank, LENGTH_PATTERN["rank"])
            and is_correct_length(datetime, LENGTH_PATTERN["datetime"])):
        return error(5)

    if not is_rank_format(rank):
        return error(10)

    company_id = controller.set_company_for_new_application(
        session["user_id"], company_name, project_id)
    if company_id is None:
        return error(14)

    controller.create_application(
        project_id, company_id, role, memo, rank, application_status, datetime)

    return dashboard(project_id)


@app.route("/application_details_<application_id>", methods=["GET", "POST"])
@login_required
def application_details(application_id):
    application = controller.get_simple_application(application_id)
    stages = controller.get_process(application_id)
    return render_template("application_details.html",
                           application_id=application_id,
                           application=application,
                           stages=stages)


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

    if not (is_correct_length(role, LENGTH_PATTERN["role"])
            and is_correct_length(rank, LENGTH_PATTERN["rank"])
            and is_correct_length(memo, LENGTH_PATTERN["memo"])):
        return error(5)

    if not is_rank_format(rank):
        return error(10)

    controller.edit_application(application_id, role, rank, memo)

    return application_details(application_id)


@app.route("/new_stage_<application_id>", methods=["GET", "POST"])
@login_required
def add_stage(application_id):
    if request.method == "GET":
        return render_template("new_stage.html",
                               application_id=application_id,
                               stages=STATUS_LIST)

    date = request.form.get("stage-date")
    time = request.form.get("stage-time")
    stage_memo = set_empty_response("stage-memo")

    # Default status takes priority
    default_status = request.form.get("default-status")
    custom_status = request.form.get("custom-status")
    if not default_status and not custom_status:
        return error(13)
    type = default_status
    if not default_status:
        type = custom_status

    if not date and not time:
        datetime = ""
    elif not time:
        return error(11)
    else:
        if not is_time_format(time):
            return error(8)
        datetime = date + " " + time

    if not (is_correct_length(datetime, LENGTH_PATTERN["datetime"])
            and is_correct_length(stage_memo, LENGTH_PATTERN["memo"])
            and is_correct_length(type, LENGTH_PATTERN["stage"])):
        return error(5)

    controller.create_stage(application_id, type, datetime, stage_memo)

    return application_details(application_id)


@app.route("/edit_stage_<stage_id>", methods=["GET", "POST"])
@login_required
def edit_stage(stage_id):
    stage = controller.get_stage(stage_id)
    if request.method == "GET":
        return render_template("edit_stage.html",
                               stage=stage,
                               status_list=STATUS_LIST)

    date = request.form.get("stage-date")
    time = request.form.get("stage-time")
    stage_memo = set_empty_response("stage-memo")

    # Default status takes priority
    default_status = request.form.get("default-status")
    custom_status = request.form.get("custom-status")
    if not default_status and not custom_status:
        return error(13)
    type = default_status
    if not default_status:
        type = custom_status

    if not date and not time:
        datetime = ""
    elif not date or not time:
        return error(11)
    else:
        if not is_time_format(time):
            return error(8)
        datetime = date + " " + time

    if not (is_correct_length(datetime, LENGTH_PATTERN["datetime"])
            and is_correct_length(stage_memo, LENGTH_PATTERN["memo"])
            and is_correct_length(type, LENGTH_PATTERN["stage"])):
        return error(5)

    controller.edit_stage(stage_id, type, datetime, stage_memo)

    return application_details(stage.application_id)


@app.route("/company_<company_id>", methods=["GET", "POST"])
@login_required
def company_details(company_id):
    company = controller.get_company(company_id)
    history = controller.get_company_history(company_id)
    return render_template("company_details.html",
                           company=company,
                           history=history)


@app.route("/search", methods=["POST"])
@login_required
def search():
    keyword = request.form.get("q")
    if not keyword:
        return error(1)
    if not is_correct_length(keyword, LENGTH_PATTERN["company_name"]):
        return error(5)
    results = controller.search_company(session["user_id"], keyword)
    return render_template("search_result.html",
                           keyword=keyword,
                           results=results)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username-login")
    password = request.form.get("password-login")

    if not username or not password:
        return error(1)
    if not is_valid_characters([username, password]):
        return error(0)

    if not (is_correct_length(username, LENGTH_PATTERN["username"])
            and is_correct_length(password, LENGTH_PATTERN["password"])):
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

    if not is_valid_characters([username, password, confirmation]):
        return error(0)

    if not (is_correct_length(username, LENGTH_PATTERN["username"])
            and is_correct_length(password, LENGTH_PATTERN["password"])
            and is_correct_length(confirmation, LENGTH_PATTERN["password"])
            ):
        return error(5)

    if password != confirmation:
        return error(2)

    user = controller.get_user_by_username(username)
    if user is not None:
        return error(3)

    controller.register_user(username, generate_password_hash(password))

    user = controller.get_user_by_username(username)
    session["user_id"] = user.id

    return redirect("/")


@app.route("/check_username_<username>", methods=["POST"])
def check_username_availability(username):
    """ Used by Javascript on the login screen """
    value = controller.get_user_by_username(username)
    if value is not None:
        return "Not available"
    return "Available"


@app.route("/check_existing_<company_name>_for_<project_id>", methods=["POST"])
def check_existing_company(company_name, project_id):
    """ Used by Javascript when creating a new application """
    return controller.search_company_js(
        session["user_id"],
        company_name,
        project_id)


@app.route("/check_last_project", methods=["POST"])
def check_last_project_date():
    """ Used by Javascript when creating a new project """
    return controller.get_last_project_datetime(session["user_id"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return display_error(e.name, e.code)


for code in default_exceptions:
    """ Listen for errors """
    app.errorhandler(code)(errorhandler)
