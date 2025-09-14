import asyncio
from app.clients import mongo_clients_sync as dbs
from app.constants import COMMON_ENTITY

def entity_metric():
    common_db = dbs.get("COMMON")[COMMON_ENTITY]
    
    has_license = common_db[COMMON_ENTITY].count_documents({"data.regulatoryCompliance.0": { "$exists": True }})
    no_license_has_descr = common_db[COMMON_ENTITY].count_documents(
        { 
            "data.regulatoryCompliance": { "$size": 0 },
            "data.description": { "$ne": None }
            }
        )
    total_entities = common_db[COMMON_ENTITY].count_documents({})
    return has_license, no_license_has_descr, total_entities

