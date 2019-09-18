from ..models import User, Authorisation
from ..repositories import UserRepository, AuthorisationRepository
from contextlib import contextmanager
from datetime import datetime
from sqlalchemy import Table, String, Column, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy import insert, select, update


@contextmanager
def transactional(engine):
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()
        connection = None


class UserSQLRepository(UserRepository):
    
    users = None

    @classmethod
    def _create_table_schema(cls, metadata):
        if cls.users is not None:
            return
        cls.users = Table('users', metadata,
            Column('id', Integer(), primary_key=True),
            Column('name', String(200), nullable=False),
            Column('email', String(200),  nullable=False),
            Column('phone', String(20),  nullable=True),
        )

    def __init__(self, metadata, engine):
        self.__class__._create_table_schema(metadata)
        self.engine = engine

    def generate_id(self):
        with transactional(self.engine) as connection:
            data = connection.execute("select max(id) from users").scalar()
            raise Exception(f"{data} : {type(data)}")

    def get_by_id(self, user_id):
        with transactional(self.engine) as connection:
            dd = select([self.__class__.users]).where(self.__class__.users.c.id==user_id)
            return self._to_object(connection.execute(dd).first())
    
    def add(self, user):
        with transactional(self.engine) as connection:
            t = connection.begin()
            r = connection.execute(insert(self.__class__.users).values( **self._from_object(user)))
            t.commit()
            return r.inserted_primary_key[0]

    def update(self, user):
        with transactional(self.engine) as connection:
            t = connection.begin()
            dd = select([self.__class__.users]).where(self.__class__.users.c.id==user.id)
            user_object = self._to_object(connection.execute(dd).first())
            if not user_object:
                raise Exception("User not found")
            user_object.name = user.name
            user_object.email = user.email
            user_object.phone = user.phone
            rows_updated = connection.execute(update(self.users).where(
                self.__class__.users.c.id==user_object.id).values(**self._from_object(user_object)))
            if rows_updated:
                t.commit()
                return user_object.id
            raise Exception("Something went wrong")
 
    def _to_object(self, row):
        if not row:
            return None
        return User(row['id'], row['name'], row['email'], row['phone'])

    def _from_object(self, user_object):
        return dict(
                id=user_object.id, 
                name=user_object.name, 
                email=user_object.email, 
                phone=user_object.phone)


class AuthorisationSQLRepository(AuthorisationRepository):
    auth = None

    @classmethod
    def _create_table_schema(cls, metadata):
        if cls.auth is not None:
            return
        if UserSQLRepository.users is None:
            UserSQLRepository._create_table_schema(metadata)
        cls.auth = Table('auth', metadata,
            Column('user_id', Integer(), ForeignKey(UserSQLRepository.users.c.id)),
            Column('user_name', String(200), nullable=False),
            Column('password', String(200),  nullable=False),
            Column('roles', String(200),  nullable=True),
        )

    def __init__(self, metadata, engine):
        self.__class__._create_table_schema(metadata)
        self.engine = engine

    def get_by_user_id(self, user_id):
        with transactional(self.engine) as connection:
            dd = select([self.__class__.auth]).where(self.__class__.auth.c.user_id==user_id)
            return self._to_object(connection.execute(dd).first())

    def get_by_user_name(self, user_name):
        with transactional(self.engine) as connection:
            dd = select([self.__class__.auth]).where(self.__class__.auth.c.user_name==user_name)
            return self._to_object(connection.execute(dd).first())

    def add(self, authorisation):
        with transactional(self.engine) as connection:
            t = connection.begin()
            r = connection.execute(insert(self.__class__.auth).values( **self._from_object(authorisation)))
            t.commit()
            return authorisation.user_id

    def update(self, authorisation):
        with transactional(self.engine) as connection:
            t = connection.begin()
            dd = select([self.__class__.auth]).where(self.__class__.auth.c.user_id==authorisation.user_id)
            auth_object = self._to_object(connection.execute(dd).first())
            if not auth_object:
                raise Exception("Auth not found")
            auth_object.user_name = authorisation.user_name
            auth_object.password = authorisation.password
            auth_object.roles = authorisation.roles
            rows_updated = connection.execute(update(self.auth).where(
                self.__class__.auth.c.user_id==auth_object.user_id).values(**self._from_object(auth_object)))
            if rows_updated:
                t.commit()
                return auth_object.user_id
            raise Exception("Something went wrong")
 
    def _to_object(self, row):
        if not row:
            return None
        return Authorisation(row['user_id'], row['user_name'], row['password'], row['roles'].split(','))

    def _from_object(self, auth_object):
        return dict(
                user_id=auth_object.user_id, 
                user_name=auth_object.user_name, 
                password=auth_object.password, 
                roles=','.join(auth_object.roles))


