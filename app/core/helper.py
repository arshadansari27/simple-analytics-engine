"""
HELPER module to get intervals
"""

from functools import partial
from datetime import timedelta, datetime
from collections import OrderedDict, defaultdict
import calendar


def divide_data_in_intervals(events, period):
    """
    Divide the given events into intervals
    """
    events = list(events)
    max_event_timestamp = max([e.timestamp for e in events])
    min_event_timestamp = min([e.timestamp for e in events])
    intervals_dict = OrderedDict()
    for u in PERIOD_DICT[period](min_event_timestamp, max_event_timestamp):
        intervals_dict[u] = {
            'project': defaultdict(int), 
            'uri': defaultdict(int),
            'total': 0,
        }
    for event in events:
        formatted_date = DATE_FORMAT[period](event.timestamp)
        intervals_dict[formatted_date]['total'] += 1
        intervals_dict[formatted_date]['project'][event.project_id] += 1
        intervals_dict[formatted_date]['uri'][event.uri] += 1
    #NOTE: This additional check is to reduce data size for demonstration purposes
    _intervals_dict = {u: dd for u, dd in intervals_dict.items() if dd['total'] > 0}
    return _intervals_dict


def less_than_month_intervals(timestamp_from, timestamp_to, diff, date_formatter):
    """
    Get all the dates representing each period in range
    """
    intervals = []
    start = timestamp_from
    stop = timestamp_from + diff
    intervals.append(start)
    while stop < timestamp_to:
        intervals.append(stop)
        start = stop
        stop += diff
    intervals.append(stop)
    return [date_formatter(i) for i in intervals]


def yearly_interval(timestamp_from, timestamp_to, date_formatter):
    """
    Get all the dates representing each year in range
    """
    if timestamp_to < timestamp_from:
        raise Exception(f"Invalid from {timestamp_from} and to {timestamp_to}")
    intervals = []        
    for year in range(timestamp_from.year, timestamp_to.year + 1):
        intervals.append(datetime(year, 1, 1))
    return [date_formatter(i) for i in intervals]


def monthly_interval(timestamp_from, timestamp_to, date_formatter):
    """
    Get all the dates representing each months in range
    """
    if timestamp_to < timestamp_from:
        raise Exception(f"Invalid from {timestamp_from} and to {timestamp_to}")
    if timestamp_from.year == timestamp_to.year and timestamp_from.month == timestamp_to.month:
        return [timestamp_from]
    start = timestamp_from
    stop = timestamp_to
    intervals = [start]
    interval = add_months(start, 1)
    while interval < stop:
        intervals.append(interval)
        interval = add_months(start, 1)
    intervals.append(interval)
    return [date_formatter(i) for i in intervals]


def add_months(sourcedate, months):
    """
    Add Months to date
    """
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


DATE_FORMAT = {
    'hourly': lambda u: u.strftime('%H%d%m%Y'),
    'daily': lambda u: u.strftime('%d%m%Y'),
    'weekly': lambda u: "{}{}".format(u.day // 4, u.strftime('%m%Y')),
    'monthly': lambda u: u.strftime('%m%Y'),
    'yearly': lambda u: u.strftime('%Y'),
}


PERIOD_DICT = {
    'hourly': partial(less_than_month_intervals, diff=timedelta(hours=1), date_formatter=DATE_FORMAT['hourly']),
    'daily': partial(less_than_month_intervals, diff=timedelta(days=1), date_formatter=DATE_FORMAT['daily']),
    'weekly': partial(less_than_month_intervals, diff=timedelta(weeks=1), date_formatter=DATE_FORMAT['weekly']),
    'monthly': partial(monthly_interval, date_formatter=DATE_FORMAT['monthly']),
    'yearly': partial(yearly_interval, date_formatter=DATE_FORMAT['yearly']),
}

