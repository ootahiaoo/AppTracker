from application import app, controller
from application.model import User
from application.helpers import login_required, status
from flask import Flask, flash, redirect, render_template, request, session
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


@app.route("/dashboard/<project_id>", methods=["GET", "POST"])
@login_required
def dashboard(project_id):
    # Merge requests?
    project = controller.get_project(project_id)
    applications = controller.get_all_applications(project_id)
    return render_template("dashboard.html", project=project, applications=applications)


@app.route("/<project_id>/new_application", methods=["GET", "POST"])
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

    return redirect("/dashboard/" + project_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return "must provide both username and password"

    user = controller.get_user_by_username(username)

    if not user or not check_password_hash(user.hash, password):
        return "invalid username and/or password"

    session["user_id"] = user.id

    return redirect("/")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username_register")
    password = request.form.get("password_register")
    confirmation = request.form.get("confirmation_register")

    if not username or not password or not confirmation:
        return "must provide both username and password"

    if password != confirmation:
        return "confirmation did not match password"

    user = controller.get_user_by_username(username)
    if user != None:
        return "username is already used"

    controller.register_user(username, generate_password_hash(password))

    user = controller.get_user_by_username(username)
    session["user_id"] = user.id

    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
