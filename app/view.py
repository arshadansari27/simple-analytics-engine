from dateutil import parser
from flask import Flask, request, jsonify
from .ioc_config import create_context
from .auth.models import User
from functools import wraps
import uuid, traceback


app = Flask(__name__)
context = create_context('main.db')
event_service, auth_service = context.event_service, context.auth_service
TOKENS = {}


def login_required(func):

    @wraps(func)
    def decorate(*args, **kwargs):
        global TOKENS
        token = request.args['token']
        if token not in TOKENS:
            return jsonify(dict(msg='Not authenticated')), 401
        try:
            return jsonify(func(*args, **kwargs)), 200
        except Exception as e:
            if getattr(e, 'authentication_error', False):
                return jsonify(dict(msg='Not authenticated')), 401
            traceback.print_exc()
            return jsonify(dict(msg='Some error occured', error=str(e))), 500
    return decorate


@app.route('/users/add', methods=['POST'])
@login_required
def add_user():
    global TOKENS
    data = request.json
    name = data['name']
    email = data['email']
    phone = data['phone']
    user_name = data['user_name']
    password = data['password']
    user = auth_service.add(name, email, user_name, password)
    return dict(user_id=user.id)


@app.route('/users/change-password/<user_id>', methods=['POST'])
@login_required
def change_password(user_id):
    data = request.json
    old_password = data['old_password']
    new_password = data['new_password']
    user = auth_service.change_password(user_id, old_password, new_password)
    return dict(user_id=user.id, message="Changed password successfully")


@app.route('/users/authenticate', methods=['GET'])
def authenticate():
    global TOKENS
    data = request.json
    user_name = data['user_name']
    password = data['password']
    user = auth_service.authenticate(user_name, password)
    token = uuid.uuid4()
    TOKENS[str(token)] = user.id
    return jsonify(dict(token=token, user_id=user.id))


@app.route('/projects/add', methods=['POST'])
@login_required
def add_project():
    global TOKEN
    data = request.json
    token = request.args['token']
    user_id = TOKENS[token]
    name = data['name']
    description = data['description']
    project_id = event_service.add_project(user_id, name, description)
    return {'message': 'Created Project Successfully', 'project_id': project_id}

@app.route('/projects/change/<project_id>/<detail>', methods=['POST'])
@login_required
def change_project_details(project_id, detail):
    global TOKENS
    data = request.json
    token = request.args['token']
    user_id = TOKENS[token]
    if detail == 'name':
        new_name = data['new_name']
        project_id = event_service.change_project_name(user_id, project_id, new_name)
        return {'message': 'Updated Project Name Successfully', 'project_id': project_id}
    else:
        new_description = data['new_description']
        project_id = event_service.change_project_description(user_id, project_id, new_description)
        return {'message': 'Updated Project Description Successfully', 'project_id': project_id}


@app.route('/projects', methods=['GET'])
@login_required
def projects():
    global TOKENS
    token = request.args['token']
    user_id = TOKENS[token]
    return {'projects': [u.to_json() for u in event_service.get_all_projects(user_id)]}

@app.route('/projects/<project_id>', methods=['GET'])
@login_required
def project(project_id):
    return {'project': event_service.get_project(project_id).to_json()}

@app.route('/events/<project_id>', methods=['GET'])
@login_required
def events(project_id):
    token = request.args['token']
    timestamp_from, timestamp_to = None, None
    if request.json['from']:
        timetamp_from = parser.parse(request.json['from']).replace(tzinfo=pytz.UTC)
    if request.json['to']:
        timetamp_to = parser.parse(request.json['to']).replace(tzinfo=pytz.UTC)
    user_id = TOKENS[token]
    events = event_service.get_all_events(project_id, timestamp_from, timestamp_to)
    project = event_service.get_project(project_id)
    response = {'events': [u.to_json() for u in events], 'project': project.to_json()}
    return response


@app.route('/events/add', methods=['POST'])
@login_required
def add_event():
    global TOKENS
    token = request.args['token']
    user_id = TOKENS[token]
    project_id = request.json['project_id']
    uri = request.json['uri']
    event_type = request.json['event_type']
    description = request.json['description']
    timestamp = parser.parse(request.json['timestamp'])
    event_id = event_service.add_event(user_id, project_id, timestamp, event_type, uri, description)
    return {'message': "successfully added event", 'event_id': event_id}
