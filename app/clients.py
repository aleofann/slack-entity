import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from slack_sdk.web import WebClient
import requests
from app.utils.parsers import read_from_json, load_template
from app.constants import COMMON_LABEL, COMMON_TAGS, COMMON_TYPES, COMMON_ENTITY, COMMON_PAYMENT_SYSTEM, COMMON_SERVICE

dir_path = os.path.dirname(os.path.realpath(__file__))

languages_map = read_from_json(os.path.join(dir_path, "..", "templates", "lang.json"), "name", "name")
countries = read_from_json(os.path.join(dir_path, "..", "templates", "country.json"), 'name', 'code')
entity_json = load_template(os.path.join(dir_path, "..", "templates", "entity.json"))

# Mongo clients
mongo_clients_async = {}
mongo_clients_sync = {}

# Bearer
_bearer_token = {
    "token": None,
    "expires_at": 0
}

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

# with mongo_clients_sync.get("COMMON").db[COMMON_LABEL][COMMON_TAGS]

tags = {doc["name"]: doc["_id"] for doc in mongo_clients_sync.get("COMMON")[COMMON_LABEL][COMMON_TAGS].find({})}
types = {doc["name"]: doc["_id"] for doc in mongo_clients_sync.get("COMMON")[COMMON_LABEL][COMMON_TYPES].find({})}
services = {doc["name"]: doc["_id"] for doc in mongo_clients_sync.get("COMMON")[COMMON_ENTITY][COMMON_SERVICE].find({})}
systems = {doc["systemName"]: doc["_id"] for doc in mongo_clients_sync.get("COMMON")[COMMON_ENTITY][COMMON_PAYMENT_SYSTEM].find({})}


print(f'INFO: Number of clients - {len(mongo_clients_async)}')

# Slack clients 
slack_clients = {}
for key, value in os.environ.items():
    if key.startswith("SLACK_TOKEN_"):
        client_name = key.replace("SLACK_TOKEN_", "").upper()
        slack_clients[client_name] = WebClient(token=value)

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
        return _bearer_token["token"]
    
    except Exception as e:
        _bearer_token["token"] = None
        return None



