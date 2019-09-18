from flask import Flask, request
from .ioc_config import create_context
from .auth.models import User


app = Flask(__name__)
context = create_context('main.db', lambda u: User(u, 'test-name', 'test-email', 'test-phone'))
event_service = context.event_service


@app.route('/add-project', methods=['POST'])
def add_project():
    data = request.json
    name = data['name']
    description = data['description']
    event_service.add_project(1, name, description)
    return 'ok'


@app.route('/change-project-details/<detail>', methods=['POST'])
def change_project_details(detail):
    data = request.json()
    if detail == 'name':
        pass # change project name
    else:
        pass # change projet detail 
    return 'ok'


@app.route('/projects/<user_id>', methods=['GET'])
def projects(user_id):
    return 'ok'

@app.route('/project/<user_id>/<project_id>', methods=['GET'])
def project(user_id, project_id):
    return 'ok'


@app.route('/events/<user_id>/<project_id>', methods=['GET'])
def events(user_id, project_id):
    return 'ok'


@app.route('/add-events', methods=['POST'])
def add_event():
    data = request.json()
    print(data)
    return 'ok'

