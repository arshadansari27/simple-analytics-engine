from ..models import AnalyticalEvent, Project, EventStats
from ..repositories import EventStatsRepository
import pytz


EVENT_STATS_COLL = 'event_stats'

class EventStatsMongoRepository(EventStatsRepository):


    def __init__(self, db):
        self.db = db

    def upsert_event_stat(self, event_stat):
        global EVENT_STATS_COLL
        self._check_period(event_stat.period)
        self.db[EVENT_STATS_COLL].update(
            {
                'user_id': event_stat.user_id,
                'period': event_stat.period,
                'project_id': event_stat.project_id,
                'interval': event_stat.interval,
            },
            {
                '$set': {

                    'count_total': event_stat.count_total, 
                    'count_event_types': event_stat.count_event_types, 
                    'count_uris': event_stat.count_uris, 
                }
            },
            True 
        )

    def get_all_stats(self, user_id, period, timestamp_from, timestamp_to):
        raise NotImplementedError

    def get_project_stats(self, project_id, period, timestamp_from, timestamp_to):
        self._check_period(period)
        query = {
            'project_id': project_id,
            'period': period,
            'interval':  {
                '$gte': timestamp_from.replace(tzinfo=pytz.UTC),
                '$lte': timestamp_to.replace(tzinfo=pytz.UTC),
            }
        }
        docs = self.db[EVENT_STATS_COLL].find(query)
        data = []
        for doc in docs:
            data.append(EventStats(
                doc['user_id'],
                doc['period'],
                doc['interval'].replace(tzinfo=pytz.UTC),
                doc['project_id'],
                doc['count_total'],
                doc['count_uris'],
                doc['count_event_types'],
            ))
        return data

    def _check_period(self, period):
        if period not in EventStats.PERIODS:
            raise Exception(
                f"Invalid period = {period}, allowed = {EventStats.PERIODS}"
            )
