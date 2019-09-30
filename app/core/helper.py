"""
HELPER module to get intervals
"""

from datetime import timedelta

def generate_interval(period, timestamp):
    if period == 'hourly':
        timestamp =  timestamp.replace(minute=0, second=0, microsecond=0)
        return timestamp
    if period == 'daily':
        timestamp =  timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        return timestamp
    if period == 'weekly':
        diff = timedelta(days=timestamp.isoweekday())
        timestamp = timestamp - diff
        timestamp =  timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        return timestamp
    if period == 'monthly':
        timestamp =  timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return timestamp
    if period == 'yearly':
        timestamp =  timestamp.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return timestamp
    raise Exception(f"Invalid Period = {period}")


def generate_interval_range(period, timestamp_from, timestamp_to):
    timestamps = []
    if period == 'hourly':
        diff = timedelta(seconds=3600)
    if period == 'daily':
        diff = timedelta(days=1)
    if period == 'weekly':
        diff = timedelta(days=7)
    if period == 'monthly':
        diff = timedelta(days=31)
    if period == 'yearly':
        diff = timedelta(days=365)
    timestamp = timestamp_from
    while timestamp < timestamp_to:
        it = generate_interval(period, timestamp)
        timestamps.append(it)
        timestamp += diff
    return timestamps
