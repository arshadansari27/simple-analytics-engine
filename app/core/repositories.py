"""
Repository Interfaces
"""


import abc


class AnalyticalEventRepository(metaclass=abc.ABCMeta):
    """ Analytical Event Repository Interface """

    @abc.abstractmethod
    def generate_id(self):
        ''' Generate Id '''

    @abc.abstractmethod
    def get_all_for_project(self, project_id, timestamp_from, timestamp_to):
        """
        Get all for project by id
        """

    @abc.abstractmethod
    def get_by_id(self, event_id):
        """
        Get event by id
        """

    @abc.abstractmethod
    def add(self, event):
        """
        Add event
        """


class ProjectRepository(metaclass=abc.ABCMeta):
    """ Project Repository Interface """

    @abc.abstractmethod
    def generate_id(self):
        """
        Generate Id
        """

    @abc.abstractmethod
    def get_by_id(self, project_id):
        """
        Get by id
        """

    @abc.abstractmethod
    def get_all(self, user_id):
        """
        Get all
        """

    @abc.abstractmethod
    def upsert(self, project):
        """
        Upsert project
        """


class EventStatsRepository(metaclass=abc.ABCMeta):
    """ Analytical Event Repository Interface """

    @abc.abstractmethod
    def upsert_event_stat(self, event_stat):
        pass

    @abc.abstractmethod
    def get_project_stats(self, project_id, period, timestamp_from, timestamp_to):
        """ 
        Get project stats: period = hourly, daily, weekly, monthly, yearly
        """
