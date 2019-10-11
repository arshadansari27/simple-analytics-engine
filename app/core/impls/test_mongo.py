import pytest
import pymongo
from ..models import EventStats
from ..helper import generate_interval
from .mongo import EventStatsMongoRepository
import pytz
from datetime import datetime


@pytest.fixture
def stats_repository():
    mongo_client = pymongo.MongoClient(host='127.0.0.1', port=27017)
    db = mongo_client['test_sae']
    return EventStatsMongoRepository(db)

def test_mongo(stats_repository: EventStatsMongoRepository):
    timestamp = datetime.now(tz=pytz.UTC)
    ts = generate_interval('hourly', timestamp)
    stats = EventStats(1, 'hourly', ts, 1, 1, {'1': 1}, {'1': 1})
    stats_repository.upsert_event_stat(stats)
    assert len(stats_repository.get_project_stats(1, 'hourly', ts, ts)) > 0