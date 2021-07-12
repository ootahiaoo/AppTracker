from application import app
import json
import sqlite3 as sql


class User(object):
    def __init__(self, id, username, hash):
        self.id = id
        self.username = username
        self.hash = hash

    @classmethod
    def from_json(cls, json_string):
        """
        Convert to python object using JSON
        https://www.youtube.com/watch?v=hJ2HfejqppE
        """
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
    def __init__(self, id, project_id, name, company_id, role, application_memo, rank, company_name, type, date):
        self.id = id
        self.project_id = project_id
        self.project_name = name
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


class Company(object):
    def __init__(self, id, company_name, company_memo):
        self.id = id
        self.company_name = company_name
        self.company_memo = company_memo

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)


class Database(object):
    def __init__(self):
        self.db_connection = None

    def __enter__(self):
        connection = sql.connect("application/track.db")
        connection.row_factory = dict_factory
        self.db_connection = connection
        return self.db_connection

    def __exit__(self, type, value, traceback):
        self.db_connection.close()


def dict_factory(cursor, row):
    """
    Convert the result to a dictionary including the column names
    https://stackoverflow.com/a/3300514/
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def register_user(username, hashed_password):
    with Database() as db:
        db.execute("INSERT INTO users(username, hash) VALUES(?, ?)",
                   (username, hashed_password))
        db.commit()


def get_user_with_id(id):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT * FROM users WHERE id = ?", (id,)).fetchone()
        if result != None:
            return User.from_json(json.dumps(result))
    return None


def get_user_with_username(username):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if result != None:
            return User.from_json(json.dumps(result))
    return None


def create_project(user_id, created_on, name, project_memo):
    with Database() as db:
        db.execute("INSERT INTO projects(user_id, created_on, name, project_memo) VALUES(?, ?, ?, ?)",
                   (user_id, created_on, name, project_memo))
        db.commit()


def edit_project(project_id, name, started_on, ended_on, project_memo):
    with Database() as db:
        db.execute("UPDATE projects SET name = ?, started_on = ?, ended_on = ?, project_memo = ? WHERE id = ?",
                   (name, started_on, ended_on, project_memo, project_id))
        db.commit()


def get_project(project_id):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if result != None:
            return Project.from_json(json.dumps(result))
    return None


def get_all_projects(user_id):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT * FROM projects WHERE user_id = ? ORDER BY created_on DESC", (user_id,)).fetchall()
        if len(result) != 0:
            projects = []
            for row in result:
                project = Project.from_json(json.dumps(row))
                projects.append(project)
            return projects
    return None


def create_company(company_name):
    with Database() as db:
        db.execute("INSERT INTO company(company_name) VALUES(?)",
                   (company_name,))
        db.commit()


def search_company(company_name):
    with Database() as db:
        cursor = db.cursor()
        company_name = "%" + company_name + "%"
        result = cursor.execute(
            "SELECT * FROM company WHERE company_name LIKE ?", (company_name,)).fetchall()
        if len(result) != 0:
            companies = []
            for row in result:
                company = Company.from_json(json.dumps(row))
                companies.append(company)
            return companies
    return None


def search_company_js(company_name):
    with Database() as db:
        cursor = db.cursor()
        company_name = "%" + company_name + "%"
        result = cursor.execute(
            "SELECT * FROM company WHERE company_name LIKE ?", (company_name,)).fetchone()
        return json.dumps(result)
    return None


def get_company_id(company_name):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT id FROM company WHERE company_name = ?", (company_name,)).fetchone()
        if result != None:
            return result["id"]
    return None


def get_company(company_id):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT * FROM company WHERE id = ?", (company_id,)).fetchone()
        if result != None:
            return Company.from_json(json.dumps(result))
    return None


def create_application(project_id, company_id, role, memo, rank):
    with Database() as db:
        db.execute("INSERT INTO applications(project_id, company_id, role, application_memo, rank) VALUES(?, ?, ?, ?, ?)",
                   (project_id, company_id, role, memo, rank))
        db.commit()


def get_simple_application(application_id):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT company_name, role, application_memo FROM applications JOIN company ON company.id = applications.company_id WHERE applications.id = ?", (application_id,)).fetchone()
        return result


def get_application_id(project_id, company_id):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT id FROM applications WHERE project_id = ? AND company_id = ?", (project_id, company_id)).fetchone()
        if result != None:
            return result["id"]
    return None


def get_application(application_id):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute("SELECT id, project_id, name, company_id, role, application_memo, rank, company_name, type, date FROM (SELECT * FROM applications JOIN company ON company.id = applications.company_id JOIN stage ON stage.application_id = applications.id JOIN projects ON projects.id = applications.project_id GROUP BY applications.id) WHERE id = ?", (application_id,)).fetchone()
        if result != None:
            return Application.from_json(json.dumps(result))
    return None


def get_all_applications(project_id):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute("SELECT id, project_id, name, company_id, role, application_memo, rank, company_name, type, date FROM (SELECT * FROM applications JOIN company ON company.id = applications.company_id JOIN stage ON stage.application_id = applications.id JOIN projects ON projects.id = applications.project_id ORDER BY stage.id DESC) WHERE project_id = ? GROUP BY application_id ORDER BY rank", (project_id,)).fetchall()
        if len(result) != 0:
            applications = []
            for row in result:
                application = Application.from_json(json.dumps(row))
                applications.append(application)
            return applications
    return None


def get_company_history(company_id):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute("SELECT id, project_id, name, company_id, role, application_memo, rank, company_name, type, date FROM (SELECT * FROM applications JOIN company ON company.id = applications.company_id JOIN stage ON stage.application_id = applications.id JOIN projects ON projects.id = applications.project_id ORDER BY stage.id DESC) WHERE company_id = ? GROUP BY project_id", (company_id,)).fetchall()
        if len(result) != 0:
            applications = []
            for row in result:
                application = Application.from_json(json.dumps(row))
                applications.append(application)
            return applications
    return None


def edit_application(application_id, role, rank, memo):
    with Database() as db:
        db.execute("UPDATE applications SET role = ?, rank = ?, application_memo = ? WHERE id = ?",
                   (role, rank, memo, application_id))
        db.commit()


def create_stage(application_id, status, datetime, stage_memo):
    with Database() as db:
        db.execute("INSERT INTO stage (application_id, type, date, stage_memo) VALUES(?, ?, ?, ?)",
                   (application_id, status, datetime, stage_memo))
        db.commit()


def get_stage(stage_id):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT * FROM stage WHERE id = ?", (stage_id,)).fetchone()
        if result != None:
            return Stage.from_json(json.dumps(result))
    return None


def get_process(application_id):
    with Database() as db:
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT * FROM stage WHERE application_id = ? ORDER BY id DESC", (application_id,)).fetchall()
        if len(result) != 0:
            stages = []
            for row in result:
                stage = Stage.from_json(json.dumps(row))
                stages.append(stage)
            return stages
    return None


def update_stage(stage_id, type, date, stage_memo):
    with Database() as db:
        db.execute("UPDATE stage SET type = ?, date = ?, stage_memo = ? WHERE id = ?",
                   (type, date, stage_memo, stage_id))
        db.commit()
