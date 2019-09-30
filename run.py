from app.ioc_config import create_context
context, app, celery = create_context(dict(db_name='main'))
from app.daemons import update_event
from app.view import *

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5555, debug=True)