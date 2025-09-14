import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from slack_sdk.web import WebClient
import requests
import logging

log = logging.getLogger(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))

# Mongo clients
mongo_clients_async = {}
mongo_clients_sync = {}
slack_clients = {}

for key, value in os.environ.items():
    if key.startswith("MONGO_URI_"):
        client_name = key.replace("MONGO_URI_", "")
        
        if client_name == "COMMON":
           sync_client = MongoClient(value)
           mongo_clients_sync[client_name] = sync_client
           continue 
        # async client
        async_client = AsyncIOMotorClient(value)
        mongo_clients_async[client_name] = async_client.get_default_database()

        # sync client
        sync_client = MongoClient(value)
        mongo_clients_sync[client_name] = sync_client.get_default_database()

print(f'INFO: Number of clients - {len(mongo_clients_async)}')

# Slack clients 
for key, value in os.environ.items():
    if key.startswith("SLACK_TOKEN_"):
        client_name = key.replace("SLACK_TOKEN_", "").upper()
        slack_clients[client_name] = WebClient(token=value)

# Bearer
_bearer_token = {
    "token": None,
    "expires_at": 0
}

def get_bearer(force_refresh: bool = False):
    if not force_refresh and _bearer_token["token"]:
        return _bearer_token["token"]
    
    headers = {
        "email": os.environ.get("email"),
        "password": os.environ.get("password")
    }
    try:
        
        res = requests.post(os.environ.get("auth_api"), json=headers)
        res.raise_for_status()

        new_token = res.json()["data"]["token"]
        _bearer_token["token"] = new_token
        return new_token
    
    except Exception as e:
        _bearer_token["token"] = None
        return None



