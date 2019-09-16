import abc


class AnalyticalEventRepository(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate_id(self):
        pass

    @abc.abstractmethod
    def get_all_for_project(self, project_id, timestamp_from, timestamp_to):
        pass

    @abc.abstractmethod
    def get_by_id(self, event_id):
        pass

    @abc.abstractmethod
    def add(self, event):
        pass


class ProjectRepository(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate_id(self):
        pass

    @abc.abstractmethod
    def get_by_id(self, project_id):
        pass

    @abc.abstractmethod
    def get_all(self, user_id):
        pass

    @abc.abstractmethod
    def upsert(self, project):
        pass


