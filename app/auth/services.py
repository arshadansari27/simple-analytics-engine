from .models import Authorisation, User
import hashlib



class AuthService:

    def __init__(self, user_repository, auth_repository):
        self.user_repository = user_repository
        self.auth_repository = auth_repository

    def add(self, name, email, phone, user_name, password, roles=[]):
        auth = self.auth_repository.get_by_user_name(user_name) 
        if auth:
            raise UserAlreadyExists(user_name)
        user_id = self.user_repository.generate_id()
        user = User(user_id, name, email, phone)
        self.user_repository.add(user)
        _password = hashlib.md5(password.encode('utf-8')).hexdigest()
        auth = Authorisation(user.id, user_name, _password, roles)
        self.auth_repository.add(auth)
        user = self._get_hydrated_user_by_id(user_id)
        return user

    def get(self, user_id):
        return self._get_hydrated_user_by_id(user_id)

    def authenticate(self, user_name, password):
        _password = hashlib.md5(password.encode('utf-8')).hexdigest()
        auth = self.auth_repository.get_by_user_name(user_name)
        if auth.password != _password:
            raise AuthenticationFailedError(user_name)
        return self._get_hydrated_user_by_id(auth.user_id)        

    def change_password(self, user_id, old_password, new_password):
        user = self._get_hydrated_user_by_id(user_id)        
        _old_password = hashlib.md5(old_password.encode('utf-8')).hexdigest()
        if user.auth.password != _old_password:
            raise AuthenticationFailedError(user.user_name)
        _new_password = hashlib.md5(new_password.encode('utf-8')).hexdigest()
        user.auth.password = _new_password
        self.auth_repository.update(user.auth)
        return user

    def add_role(self, user_id, role):
        user = self._get_hydrated_user_by_id(user_id)        
        if role not in user.roles:
            user.roles.append(role)
            self.auth_repository.update(user.auth)
        return user

    def remove_role(self, user_id, role):
        user = self._get_hydrated_user_by_id(user_id)        
        if role in user.roles:
            user.roles.remove(role)
            self.auth_repository.update(user.auth)
        return user

    def _get_hydrated_user_by_id(self, user_id):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id)
        auth = self.auth_repository.get_by_user_id(user_id)
        if not auth:
            raise AuthNotFound(user_id)
        user.auth = auth
        return user


class UserNotFound(Exception):

    def __init__(self, user_id):
        super(Exception, self).__init__(f"User not found {user_id}")

class AuthNotFound(Exception):

    def __init__(self, user_id):
        super(Exception, self).__init__(f"Auth not found {user_id}")

class UserAlreadyExists(Exception):

    def __init__(self, user_name):
        super(Exception, self).__init__(f"User with {user_name} already exists")

class AuthenticationFailedError(Exception):

    def __init__(self, user_name):
        super(Exception, self).__init__(f"Authentication for {user_name} failed")
        self.authentication_error = True

