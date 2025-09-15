import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask
from .config import Config
from .celery_app import celery

def create_app():
    
    # Create and configure Flask
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.debug and not app.testing:
        if not os.path.exists("logs"):
            os.mkdir("logs")

        file_handler = RotatingFileHandler("logs/app.log", maxBytes=10240, backupCount=5)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        ))

        main_logger = logging.getLogger()
        main_logger.setLevel(logging.INFO)
        main_logger.addHandler(file_handler)

        logging.info("App running")
        
    # Celery init
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"]
    )
    celery.conf.include = [
        "app.tasks.slash_commands",
        "app.tasks.file_tasks",
        "app.tasks.scheduled_procedures",
    ]

    celery.conf.task_routes = {"app.tasks.*": {"queue": "debug_queue"}}
    celery.conf.task_default_queue = "debug_queue"
    celery.conf.beat_schedule = {
        "update-data-maps-every-hour": {
            "task": "update.data.maps",
            "schedule": 3600.0, 
        },
    }
    from app.data_cache import update_data_maps
    update_data_maps()
    
    # blueprints
    from .api.routes import events_bp, slack_bp, entity_bp
    app.register_blueprint(events_bp)
    app.register_blueprint(slack_bp)
    app.register_blueprint(entity_bp)

    return app