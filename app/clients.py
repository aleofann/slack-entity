import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from slack_sdk.web import WebClient


# Mongo clients
mongo_clients_async = {}
mongo_clients_sync = {}

for key, value in os.environ.items():
    if key.startswith("MONGO_URI_"):
        client_name = key.replace("MONGO_URI_", "")
        
        # async client
        async_client = AsyncIOMotorClient(value)
        mongo_clients_async[client_name] = async_client.get_default_database()

        # sync client
        sync_client = MongoClient(value)
        mongo_clients_sync[client_name] = sync_client.get_default_database()

print(f'INFO: Number of clients - {len(mongo_clients_async)}')

# Slack clients 
slack_clients = {}
for key, value in os.environ.items():
    if key.startswith("SLACK_TOKEN_"):
        client_name = key.replace("SLACK_TOKEN_", "").upper()
        slack_clients[client_name] = WebClient(token=value)