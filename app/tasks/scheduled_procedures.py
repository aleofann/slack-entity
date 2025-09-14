from app.celery_app import celery
from app.data_cache import update_data_maps

@celery.task(name="update.data.maps")
def update_data_maps_task():
    update_data_maps()