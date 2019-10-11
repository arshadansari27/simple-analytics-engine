import pytest
from unittest.mock import MagicMock
from collections import namedtuple
from app.auth.models import User, Authorisation
from app.core.models import Project, AnalyticalEvent, EventStats
from datetime import datetime
import json


#TODO: This is a bad hack due to module level variables. 
import app.ioc_config as ioc_config
ioc_config.context = MagicMock()
ioc_config.app = ioc_config.create_app(dict(db_name='test_view'))
ioc_config.celery = MagicMock()
import app.daemons as daemons
daemons.update_event = MagicMock()

from app.ioc_config import app
import app.view as view



@pytest.fixture
def client():
    _client = app.test_client()
    auth_service = MagicMock()
    event_service = MagicMock()
    test_user1 = User(1, 'test', 'test', 'test')
    test_user2 = User(2, 'test', 'test', 'test')
    test_user1.auth = Authorisation(1, 'test', '5f4dcc3b5aa765d61d8327deb882cf99', [])
    test_user2.auth = Authorisation(1, 'test', '5f4dcc3b5aa765d61d8327deb882cf99', [])

    auth_service.authenticate = MagicMock(return_value=test_user1)
    auth_service.add = MagicMock(return_value=test_user2)
    auth_service.change_password = MagicMock(return_value=test_user2)

    project = Project(1, 1, 'test name', 'test description')
    events = [AnalyticalEvent(1, datetime.now(), 'test', 'test', 'test', 1)]
    event_service.add_project = MagicMock(return_value=project.id)
    event_service.change_project_name = MagicMock(return_value=project.id)
    event_service.change_project_description = MagicMock(return_value=project.id)
    event_service.get_all_projects = MagicMock(return_value=[project])
    event_service.get_project = MagicMock(return_value=project)
    event_service.get_all_events = MagicMock(return_value=[e for e in events])
    event_service.add_event = MagicMock(return_value=1)
    view.event_service = event_service
    view.auth_service = auth_service
    return _client


def client_authenticate(client):
    response = client.get('/users/authenticate', json={'user_name': 'admin', 'password': 'password'}, follow_redirects=True)
    assert response.status_code == 200
    return response.json['token']

def test_add_user(client):
    token = client_authenticate(client)
    response = client.post(f"/users/add?token={token}", json={
                    'name': 'test name', 
                    'email': 'test email', 
                    'phone': 'test phone', 
                    'user_name': 'test', 
                    'password': 'password'
                }, follow_redirects=True)
    assert response.status_code == 200
    assert response.json['user_id'] is 2

def test_change_password(client):
    token = client_authenticate(client)
    response = client.post(f"/users/change-password/2?token={token}", json={
                    'old_password': 'password', 
                    'new_password': 'another_password', 
                }, follow_redirects=True)
    assert response.status_code == 200
    assert response.json['user_id'] is 2
    assert response.json['message'] == "Changed password successfully"


def test_add_project(client):
    token = client_authenticate(client)
    response = client.post(f"/projects/add?token={token}", json={
                    'name': 'test project', 
                    'description': 'test_description', 
                }, follow_redirects=True)
    print(response.json)
    assert response.status_code == 200
    assert response.json['project_id'] is 1


def test_change_project_details(client):
    token = client_authenticate(client)
    response = client.post(f"/projects/change/1/name?token={token}", json={'new_name': 'test project new'}, follow_redirects=True)
    assert response.status_code == 200
    assert response.json['project_id'] is 1
    response = client.post(f"/projects/change/1/description?token={token}", json={'new_description': 'test project description new'}, follow_redirects=True)
    assert response.status_code == 200
    assert response.json['project_id'] is 1

def test_projects(client):
    token = client_authenticate(client)
    response = client.get(f"/projects?token={token}", follow_redirects=True)
    assert response.status_code == 200
    assert response.json['projects'][0]['id'] is 1


def test_project(client):
    token = client_authenticate(client)
    response = client.get(f"/projects/1?token={token}", follow_redirects=True)
    assert response.status_code == 200
    print(response.json)
    assert response.json['project']['id'] is 1


def test_events(client):
    token = client_authenticate(client)
    response = client.get(f"/events/1?token={token}", json={'from': None, 'to': None}, follow_redirects=True)
    assert response.status_code == 200
    assert response.json['events'][0]['id'] is 1


def test_add_event(client):
    token = client_authenticate(client)
    response = client.post(f"/event/add?token={token}", json={
                    'project_id': 1, 
                    'uri': '/test', 
                    'event_type': 'test-event', 
                    'description': 'test-event description', 
                    'timestamp': datetime.now(), 
                }, follow_redirects=True)
    print(response.json)
    assert response.status_code == 200
    assert response.json['event_id'] is 1


