from .ioc_config import celery, context
from .app_events import register


event_service, auth_service, stat_service = context.event_service, context.auth_service, context.stats_service


@celery.task
def update_event(user_id, project_id, event_id):
    user = auth_service.get(user_id)
    project = event_service.get_project(project_id)
    event = event_service.get_event(event_id)
    print(f"{user.name} added event on project: {project.name} of type {event.event_type} on uri {event.uri}")
    stat_service.add_event_stat(user_id, project_id, event)


register('EVENT_ARRIVAL', update_event.delay)