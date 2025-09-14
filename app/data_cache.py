import logging

from app.clients import mongo_clients_sync
from app.constants import COMMON_LABEL, COMMON_TAGS, COMMON_TYPES, COMMON_ENTITY, COMMON_PAYMENT_SYSTEM, COMMON_SERVICE
from app.utils.parsers import read_from_json, load_template
import os

log = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
PROJECT_ROOT = os.path.dirname(dir_path)

TAGS = {}
TYPES = {}
SERVICES = {}
SYSTEMS = {}
LANGUAGES_MAP = {}
COUNTRIES_MAP = {}
ENTITY_TEMPLATE = {}

def update_data_maps():
    global TAGS, TYPES, SERVICES, SYSTEMS, LANGUAGES_MAP, COUNTRIES_MAP, ENTITY_TEMPLATE
    
    log.info("Attempting to update data maps...")
    try:
        lang_path = os.path.join(PROJECT_ROOT, "templates", "lang.json")
        country_path = os.path.join(PROJECT_ROOT, "templates", "country.json")
        entity_path = os.path.join(PROJECT_ROOT, "templates", "entity.json")

        LANGUAGES_MAP = read_from_json(lang_path, "name", "name")
        COUNTRIES_MAP = read_from_json(country_path, 'name', 'code')
        ENTITY_TEMPLATE = load_template(entity_path)


        common_client = mongo_clients_sync.get("COMMON")
        if not common_client:
            log.error("COMMON database client not found. Cannot update maps from DB.")
            return

        label_db = common_client[COMMON_LABEL]
        entity_db = common_client[COMMON_ENTITY]

        TAGS = {doc["name"]: doc["_id"] for doc in label_db[COMMON_TAGS].find({})}
        TYPES = {doc["name"]: doc["_id"] for doc in label_db[COMMON_TYPES].find({})}
        SERVICES = {doc["name"]: doc["_id"] for doc in entity_db[COMMON_SERVICE].find({})}
        SYSTEMS = {doc["systemName"]: doc["_id"] for doc in entity_db[COMMON_PAYMENT_SYSTEM].find({})}
            
        log.info("Data maps updated successfully.")
    except Exception as e:
        log.error(f"Failed to update data maps: {e}", exc_info=True)