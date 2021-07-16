from application import app
from application import model
from application.model import Company, User, Project, Application, Stage
import json

"""
Fetch data from the model, handle empty result,
and transform to python object or json
"""


def get_user_by_id(id):
    result = model.get_user_with_id(id)
    if result is not None:
        return User.from_json(json.dumps(result))
    return None


def get_user_by_username(username):
    result = model.get_user_with_username(username)
    if result is not None:
        return User.from_json(json.dumps(result))
    return None


def register_user(username, hashed_password):
    model.register_user(username, hashed_password)


def create_project(user_id, created_on, name, memo):
    model.create_project(user_id, created_on, name, memo)


def edit_project(project_id, name, started_on, ended_on, project_memo):
    model.edit_project(project_id, name, started_on, ended_on, project_memo)


def get_project(project_id):
    result = model.get_project(project_id)
    if result is not None:
        return Project.from_json(json.dumps(result))
    return None


def get_last_project_datetime(user_id):
    result = model.get_last_project_datetime(user_id)
    if result is not None:
        return result["created_on"]
    return ""


def get_all_projects(user_id):
    result = model.get_all_projects(user_id)
    if not result:
        return None
    projects = []
    for row in result:
        project = Project.from_json(json.dumps(row))
        projects.append(project)
    return projects


def create_company(user_id, company_name):
    model.create_company(user_id, company_name)


def get_company_id(user_id, company_name):
    result = model.get_company_id(user_id, company_name)
    if result is not None:
        return result["id"]
    return None


def get_company(company_id):
    result = model.get_company(company_id)
    if result is not None:
        return Company.from_json(json.dumps(result))
    return None


def search_company(user_id, company_name):
    result = model.search_company(user_id, company_name)
    if not result:
        return None
    companies = []
    for row in result:
        company = Company.from_json(json.dumps(row))
        companies.append(company)
    return companies


def set_company_for_new_application(user_id, company_name, project_id):
    company = search_company(user_id, company_name)
    if not company:
        create_company(user_id, company_name)
        company_id = get_company_id(user_id, company_name)
    else:
        company_id = company[0].id
        # Check if already applied to this company in this project
        other_company_ids = model.get_all_company_ids_from_project(project_id)
        if other_company_ids:
            # https://stackoverflow.com/a/3897516
            if any(id["company_id"] == company_id for id in other_company_ids):
                return None
    return company_id


def search_company_js(user_id, company_name, project_id):
    """ Return json response to Javascript """
    result = model.search_company(user_id, company_name)
    other_company_ids = model.get_all_company_ids_from_project(project_id)
    if result and other_company_ids:
        filtered_list = [item for item in result if not any(
            id["company_id"] == item["id"] for id in other_company_ids)]
        return json.dumps(filtered_list)
    return json.dumps(result)


def create_application(project_id, company_id, role, memo, rank,
                       application_status, datetime):
    # TODO: handle error, return response
    model.create_application(project_id, company_id, role, memo, rank)
    application_id = get_application_id(project_id, company_id)
    create_stage(application_id, application_status, datetime)


def get_simple_application(application_id):
    return model.get_simple_application(application_id)


def get_application_id(project_id, company_id):
    result = model.get_application_id(project_id, company_id)
    if result is not None:
        return result["id"]
    return None


def get_application(application_id):
    result = model.get_application(application_id)
    if result is not None:
        return Application.from_json(json.dumps(result))
    return None


def get_all_applications(project_id):
    result = model.get_all_applications(project_id)
    if not result:
        return None
    applications = []
    for row in result:
        application = Application.from_json(json.dumps(row))
        applications.append(application)
    return applications


def get_company_history(company_id):
    result = model.get_company_history(company_id)
    if not result:
        return None
    applications = []
    for row in result:
        application = Application.from_json(json.dumps(row))
        applications.append(application)
    return applications


def edit_application(application_id, role, rank, memo):
    model.edit_application(application_id, role, rank, memo)


def create_stage(application_id, status, datetime, memo=""):
    model.create_stage(application_id, status, datetime, memo)


def get_process(application_id):
    result = model.get_process(application_id)
    if not result:
        return None
    stages = []
    for row in result:
        stage = Stage.from_json(json.dumps(row))
        stages.append(stage)
    return stages


def get_stage(stage_id):
    result = model.get_stage(stage_id)
    if result is not None:
        return Stage.from_json(json.dumps(result))
    return None


def edit_stage(stage_id, type, date, stage_memo):
    model.update_stage(stage_id, type, date, stage_memo)
