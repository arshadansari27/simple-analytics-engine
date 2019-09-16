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


class Project:

    def __init__(self, user_id, project_id, project_name, project_description):
        self.user_id = user_id
        self.id = project_id
        self.name = project_name
        self.description = project_description
        self._events = []

    def __repr__(self):
        return f"{self.id}: {self.name}"

