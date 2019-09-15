from ...models import AnalyticalEvent, Project
from datetime import datetime
import pytz


ANALYTICAL_EVENTS = [
    AnalyticalEvent(1, datetime.now(pytz.UTC), 'TYPE 1', '/test-uri-1', 'test descripton', 1),
    AnalyticalEvent(2, datetime.now(pytz.UTC), 'TYPE 2', '/test-uri-1', 'test descripton', 1),
    AnalyticalEvent(3, datetime.now(pytz.UTC), 'TYPE 3', '/test-uri-2', 'test descripton', 1),
    AnalyticalEvent(4, datetime.now(pytz.UTC), 'TYPE 1', '/test-uri-1', 'test descripton', 2),
    AnalyticalEvent(5, datetime.now(pytz.UTC), 'TYPE 2', '/test-uri-1', 'test descripton', 2),
    AnalyticalEvent(6, datetime.now(pytz.UTC), 'TYPE 2', '/test-uri-2', 'test descripton', 2),
]
PROJECTS = [
        Project(1, 'test project 1', 'this is a test project to be used by fixtures'),
        Project(2, 'test project 2', 'this is a test project to be used by fixtures'),
]
