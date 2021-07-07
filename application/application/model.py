from application import app
from cs50 import SQL
import json


class User(object):
    def __init__(self, id, username, hash):
        self.id = id
        self.username = username
        self.hash = hash

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)


class Project(object):
    def __init__(self, id, user_id, created_on, name, started_on, ended_on, project_memo):
        self.id = id
        self.user_id = user_id
        self.created_on = created_on
        self.name = name
        self.started_on = started_on
        self.ended_on = ended_on
        self.project_memo = project_memo

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)


class Application(object):
    def __init__(self, id, project_id, company_id, role, application_memo, rank, company_name, company_memo, application_id, type, date, stage_memo):
        self.id = id
        self.project_id = project_id
        self.company_id = company_id
        self.role = role
        self.application_memo = application_memo
        self.rank = rank
        self.company_name = company_name
        self.stage = type
        self.date = date

    @classmethod
    def from_json(cls, json_string):
        print(json_string)
        json_dict = json.loads(json_string)
        return cls(**json_dict)


class Stage(object):
    def __init__(self, id, application_id, date, type, stage_memo):
        self.id = id
        self.application_id = application_id
        self.date = date
        self.type = type
        self.stage_memo = stage_memo

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)


class Database(object):
    def __init__(self):
        self.db_connection = None

    def __enter__(self):
        self.db_connection = SQL("sqlite:///application/track.db")
        return self.db_connection

    def __exit__(self, type, value, traceback):
        self.db_connection._disconnect()


def register_user(username, hashed_password):
    with Database() as db:
        db.execute("INSERT INTO users(username, hash) VALUES(?, ?)",
                   username, hashed_password)


def get_user_with_id(id):
    with Database() as db:
        rows = db.execute("SELECT * FROM users WHERE id = ?", id)
    if len(rows) != 1:
        return None
    return User.from_json(json.dumps(rows[0]))


def get_user_with_username(username):
    with Database() as db:
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
    if len(rows) != 1:
        return None
    return User.from_json(json.dumps(rows[0]))


def create_project(user_id, created_on, name, memo):
    with Database() as db:
        db.execute("INSERT INTO projects(user_id, created_on, name, project_memo) VALUES(?, ?, ?, ?)",
                   user_id, created_on, name, memo)


def get_project(project_id):
    with Database() as db:
        rows = db.execute("SELECT * FROM projects WHERE id = ?", project_id)
    if len(rows) == 0:
        return None
    return Project.from_json(json.dumps(rows[0]))


def get_all_projects(user_id):
    with Database() as db:
        rows = db.execute(
            "SELECT * FROM projects WHERE user_id = ? ORDER BY created_on DESC", user_id)
    if len(rows) == 0:
        return None
    projects = []
    for row in rows:
        project = Project.from_json(json.dumps(row))
        projects.append(project)
    return projects


def create_company(company_name):
    with Database() as db:
        db.execute("INSERT INTO company(company_name) VALUES(?)", company_name)


def search_company(company_name):
    with Database() as db:
        rows = db.execute(
            "SELECT * FROM company WHERE company_name LIKE ?", "%" + company_name + "%")
    if len(rows) == 0:
        return None
    return rows


def get_company_id(company_name):
    with Database() as db:
        rows = db.execute(
            "SELECT id FROM company WHERE company_name = ?", company_name)
    if len(rows) == 0:
        return None
    return rows[0]["id"]


def create_application(project_id, company_id, role, memo, rank):
    with Database() as db:
        db.execute("INSERT INTO applications(project_id, company_id, role, application_memo, rank) VALUES(?, ?, ?, ?, ?)",
                   project_id, company_id, role, memo, rank)


def get_application(project_id, company_id):
    with Database() as db:
        rows = db.execute(
            "SELECT * FROM applications WHERE project_id = ? AND company_id = ?", project_id, company_id)
    if len(rows) == 0:
        return None
    return Application.from_json(json.dumps(rows[0]))


def get_application_id(project_id, company_id):
    with Database() as db:
        rows = db.execute(
            "SELECT id FROM applications WHERE project_id = ? AND company_id = ?", project_id, company_id)
    if len(rows) == 0:
        return None
    return rows[0]["id"]


def get_all_applications(project_id):
    with Database() as db:
        rows = db.execute(
            "SELECT * FROM applications JOIN company ON company.id = applications.company_id JOIN stage ON stage.application_id = applications.id WHERE project_id = ? ORDER BY rank", project_id)
    if len(rows) == 0:
        return None
    applications = []
    for row in rows:
        application = Application.from_json(json.dumps(row))
        applications.append(application)
    return applications


def create_process(application_id, status, datetime):
    with Database() as db:
        db.execute(
            "INSERT INTO stage (application_id, type, date) VALUES(?, ?, ?)", application_id, status, datetime)


def get_process(application_id):
    with Database() as db:
        rows = db.execute(
            "SELECT * FROM stage WHERE application_id = ? ORDER BY date", application_id)
    if len(rows) == 0:
        return None
    stages = []
    for row in rows:
        stage = Stage.from_json(json.dumps(row))
        stages.append(stage)
    return stages
