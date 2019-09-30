import json
from collections import defaultdict


class AnalyticalEvent:

    def __init__(self, event_id, timestamp, event_type, uri, description, project_id):
        self.id = event_id
        self.uri = uri
        self.event_type = event_type
        self.description = description
        self.project_id = project_id
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.id}: {self.event_type} @ {self.timestamp}"

    def __eq__(self, other):
        if not isinstance(other, AnalyticalEvent):
            return False
        for key in {'id', 'timestamp', 'event_type', 'uri', 'description', 'project_id'}:
            if getattr(self, key, None) != getattr(other, key, False):
                return False
        return True

    def to_json(self):
        return {
            'id': self.id, 
            'uri': self.uri, 
            'event_type': self.event_type, 
            'project_id': self.project_id, 
            'description': self.description,
            'timestamp': str(self.timestamp)
        }


class Project:

    def __init__(self, user_id, project_id, project_name, project_description):
        self.user_id = user_id
        self.id = project_id
        self.name = project_name
        self.description = project_description
        self._events = []

    def __repr__(self):
        return f"{self.id}: {self.name}"

    def __eq__(self, other):
        if not isinstance(other, Project):
            return False
        for key in {'id', 'user_id', 'name', 'description'}:
            if getattr(self, key, None) != getattr(other, key, False):
                return False
        return True

    def to_json(self):
        return {'user_id': self.user_id, 'id': self.id, 'name': self.name, 'description': self.description}


class EventStats:

    PERIODS = {'hourly', 'daily', 'weekly', 'monthly', 'yearly'}

    def __init__(self, user_id, period, interval, project_id,
                    count_total,
                    count_event_types,
                    count_uris):
        assert period in self.PERIODS
        self.user_id = user_id
        self.period = period
        self.interval = interval
        self.project_id = project_id
        self.count_event_types = count_event_types or defaultdict(int)
        self.count_uris = count_uris or defaultdict(int)
        self.count_total = count_total or 0

    def to_json(self):
        return {
            'user_id': self.user_id, 
            'period': self.period, 
            'interval': self.interval, 
            'count_total': self.count_total, 
            'project_id': self.project_id, 
            'count_event_types': self.count_event_types, 
            'count_uris': self.count_uris, 
        }

