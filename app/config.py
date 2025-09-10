import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #Celery config
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
 
 
    # Slack config
    SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
    SLACK_SECRET = os.environ.get('SLACK_SECRET')
    SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL')
    