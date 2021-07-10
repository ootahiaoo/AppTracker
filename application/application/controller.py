from application import app
from application import model


def get_user_by_id(id):
    return model.get_user_with_id(id)


def get_user_by_username(username):
    return model.get_user_with_username(username)


def register_user(username, hashed_password):
    model.register_user(username, hashed_password)


def create_project(user_id, created_on, name, memo):
    model.create_project(user_id, created_on, name, memo)


def edit_project(project_id, name, started_on, ended_on, project_memo):
    model.edit_project(project_id, name, started_on, ended_on, project_memo)


def get_project(project_id):
    return model.get_project(project_id)


def get_all_projects(user_id):
    return model.get_all_projects(user_id)


def create_company(company_name):
    model.create_company(company_name)


def get_company_id(company_name):
    return model.get_company_id(company_name)


def get_company(company_id):
    return model.get_company(company_id)


def search_company(company_name):
    return model.search_company(company_name)


def create_application(project_id, company_id, role, memo, rank, application_status, datetime):
    # TODO: handle error, return response
    model.create_application(project_id, company_id, role, memo, rank)
    application_id = get_application_id(project_id, company_id)
    create_stage(application_id, application_status, datetime)


def get_simple_application(application_id):
    return model.get_simple_application(application_id)


def get_application_id(project_id, company_id):
    return model.get_application_id(project_id, company_id)

def get_application(application_id):
    return model.get_application(application_id)


def get_all_applications(project_id):
    return model.get_all_applications(project_id)


def get_company_history(company_id):
    return model.get_company_history(company_id)


def edit_application(application_id, role, rank, memo):
    model.edit_application(application_id, role, rank, memo)


def create_stage(application_id, status, datetime, memo=""):
    model.create_stage(application_id, status, datetime, memo)


def get_process(application_id):
    return model.get_process(application_id)


def get_stage(stage_id):
    return model.get_stage(stage_id)


def edit_stage(stage_id, type, date, stage_memo):
    model.update_stage(stage_id, type, date, stage_memo)
