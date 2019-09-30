from app.view import celery


@celery.task
def update_event(user_id, project_id, event_id):
    print('[*]', user_id, project_id, event_id)