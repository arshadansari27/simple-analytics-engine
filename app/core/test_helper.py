import pytest
from datetime import datetime, timedelta
from .helper import generate_interval, generate_interval_range

def test_generate_interval():
    now = datetime.now()
    hourly = generate_interval('hourly', now)
    assert hourly.minute == 0
    assert hourly.second == 0
    assert hourly.microsecond == 0
    daily = generate_interval('daily', now)
    assert daily.hour == 0
    assert daily.minute == 0
    assert daily.second == 0
    assert daily.microsecond == 0
    weekly = generate_interval('weekly', now)
    assert weekly.day == (now - timedelta(days=now.isoweekday())).day
    assert weekly.hour == 0
    assert weekly.minute == 0
    assert weekly.second == 0
    assert weekly.microsecond == 0
    monthly = generate_interval('monthly', now)
    assert monthly.day == 1
    assert monthly.hour == 0
    assert monthly.minute == 0
    assert monthly.second == 0
    assert monthly.microsecond == 0
    yearly = generate_interval('yearly', now)
    assert yearly.month == 1
    assert yearly.day == 1
    assert yearly.hour == 0
    assert yearly.minute == 0
    assert yearly.second == 0
    assert yearly.microsecond == 0


def test_generate_interval_range():
    timestamp_from = datetime.now() - timedelta(days=1000)
    timestamp_to = datetime.now()
    
    assert 24000 < len(generate_interval_range('hourly', timestamp_from, timestamp_to)) <= 24001
    assert 1000 <= len(generate_interval_range('daily', timestamp_from, timestamp_to)) <= 1001
    assert (52 * 2) < len(generate_interval_range('weekly', timestamp_from, timestamp_to)) < (52 * 3)
    assert len(generate_interval_range('monthly', timestamp_from, timestamp_to)) > 24
    assert len(generate_interval_range('yearly', timestamp_from, timestamp_to)) == 3
