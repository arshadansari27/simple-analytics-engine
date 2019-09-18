from sqlalchemy import create_engine, MetaData 
from collections import namedtuple
from datetime import datetime
import pytz
import pytest
import os

from .sql import AuthorisationSQLRepository, UserSQLRepository
from ..models import User, Authorisation

@pytest.fixture
def context():
    try:
        os.remove('user_test.db')
    except FileNotFoundError:
        pass
    metadata = MetaData()
    engine = create_engine("sqlite:///user_test.db")
    ar = AuthorisationSQLRepository(metadata, engine)
    ur = UserSQLRepository(metadata, engine)
    UserRepositoryTuple = namedtuple("UserRepositoryTuple", ['user_repository', 'auth_repository'])
    ctx = UserRepositoryTuple(ur, ar)
    metadata.create_all(engine)
    return ctx


def test_sql(context):
    user_repository = context.user_repository
    auth_repository = context.auth_repository
    users = []
    auth = []
    users.append(User(1, "test name 1", "test email 1", "tes phone 1"))
    users.append(User(2, "test name 2", "test email 2", "tes phone 2"))
    users.append(User(3, "test name 3", "test email 3", "tes phone 3"))
    auth.append(Authorisation(1, "user_name_1",  "test_passsword", ['role 1', 'role 2']))
    auth.append(Authorisation(2, "user_name_2",  "test_passsword", ['role 3']))
    auth.append(Authorisation(3, "user_name_3",  "test_passsword", []))

    for user in users:
        assert user_repository.add(user) == user.id

    user = user_repository.get_by_id(2)
    assert user.id == 2 and user.name == 'test name 2'
    user.email = 'another test'
    user_repository.update(user)
    user = user_repository.get_by_id(2)
    assert user.email == 'another test' 

    for a in auth:
        assert auth_repository.add(a) == a.user_id


    a = auth_repository.get_by_user_name('user_name_2')
    assert a.password == 'test_passsword' and a.user_id == 2
    a.password = 'new_password'
    auth_repository.update(a)
    a = auth_repository.get_by_user_name('user_name_2')
    assert a.password == 'new_password' and a.user_id == 2

    os.remove('user_test.db')
