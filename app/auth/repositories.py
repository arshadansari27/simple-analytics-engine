import abc


class UserRepository(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_by_id(self, user_id):
        pass
    
    @abc.abstractmethod
    def add(self, user):
        pass

    @abc.abstractmethod
    def update(self, user):
        pass



class AuthorisationRepository(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_by_user_name(self, user_name):
        pass

    @abc.abstractmethod
    def get_by_user_id(self, user_id):
        pass

    @abc.abstractmethod
    def add(self, authorisation):
        pass

    @abc.abstractmethod
    def update(self, authorisation):
        pass
