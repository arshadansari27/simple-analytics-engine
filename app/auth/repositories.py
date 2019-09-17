import abc


class UserRepository(abc.ABCMeta):

    @abc.abstractmethod
    def get_by_id(self, user_id):
        pass
    
    @abc.abstractmethod
    def add(self, user):
        pass


class AuthorisationRepository(abc.ABCMeta):

    @abc.abstractmethod
    def get_by_user_name(self, user_name):
        pass

    @abc.abstractmethod
    def add(self, authorisation):
        pass
