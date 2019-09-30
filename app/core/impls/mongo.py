from ..models import AnalyticalEvent, Project, EventStats
from ..repositories import EventStatsRepository
                            

class EventStatsMongoRepository(EventStatsRepository):


    def __init__(self, connection):
        self.connection = connection

    def upsert_event_stat(self, user, project, event):
        raise NotImplementedError

    def get_all_stats(self, user_id, period, timestamp_from, timestamp_to):
        raise NotImplementedError

    def get_project_stats(self, project_id, period, timestamp_from, timestamp_to):
        raise NotImplementedError

    def _check_period(self, period):
        if period not in EventStatsMongoRepository.PERIODS:
            raise Exception(
                f"Invalid period = {period}, allowed = {EventStats.PERIODS}"
            )
