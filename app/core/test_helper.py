import pytest

from datetime import datetime
from .models import AnalyticalEvent
from .helper import divide_data_in_intervals


@pytest.fixture() 
def hourly_events_one_day():
    return [AnalyticalEvent(i, datetime(2019, 1, 1, i % 10), f'test-{i % 3}', f'/test/{i % 10}', 'test desc', 1) for i in range(100)]


@pytest.fixture() 
def hourly_events_multiple_days():
    return [AnalyticalEvent(i, datetime(2019, 1, (i % 5) + 1, i % 10), f'test-{i % 3}', f'/test/{i % 10}', 'test desc', 1) for i in range(100)]



def test_hourly_events_one_day(hourly_events_one_day):
    for interval, stats in divide_data_in_intervals(hourly_events_one_day, 'hourly').items():
        print(interval)
        print('[*]', stats)


def test_hourly_events_multiple_days(hourly_events_multiple_days):
    for interval, stats in divide_data_in_intervals(hourly_events_multiple_days, 'hourly').items():
        print(interval)
        print('[*]', stats)

