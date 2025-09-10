from flask import Flask
from .config import Config
from .celery_app import celery
from pprint import pprint

def create_app():
    
    # Create and configure Flask
    app = Flask(__name__)
    app.config.from_object(Config)


    # Celery init
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.task_routes = {'app.tasks.*': {'queue': 'debug_queue'}}
    celery.conf.task_default_queue = 'debug_queue'
    celery.conf.include = [
        'app.tasks.reports'
    ]
    
    # blueprints
    from .api.routes import events_bp, slack_bp 
    app.register_blueprint(events_bp)
    app.register_blueprint(slack_bp)
    pprint(list(app.url_map.iter_rules()))

    return app