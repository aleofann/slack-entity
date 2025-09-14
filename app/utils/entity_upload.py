import os
from bson import ObjectId
import logging
from copy import deepcopy
from dataclasses import dataclass, fields
from app.clients import mongo_clients_sync, get_bearer
from app.data_cache import (TAGS, TYPES, SERVICES, SYSTEMS, 
                            LANGUAGES_MAP, COUNTRIES_MAP, ENTITY_TEMPLATE)
from app.utils.parsers import get_countries, parse_date
from app.utils.decorators import exception_retry
from app.models.schemas import Compliance, Contacts, Departments
from app.constants import bool_map, COMMON_ENTITY
import requests 


log = logging.getLogger(__name__)

@exception_retry(retries=3, backoff=0.5)
def update_entity(entity_id, headers, data):
    res = requests.put(f'{os.environ.get("upload_api")}{entity_id}', headers=headers, json=data, timeout=10)
    res.raise_for_status()
    log.info(f"{entity_id}: {res.status_code}")
    return res.status_code

    
@exception_retry(retries=3, backoff=0.5)
def create_entity(headers, data):
    res = requests.post(os.environ.get("upload_api"), headers=headers, json=data)
    return res.status_code

def find_entity(db, entity_name):
    if not db or not entity_name:
        return None
    
    try:
        entity = db[COMMON_ENTITY][COMMON_ENTITY].find_one({'owner': entity_name}, {'_id': 1, 'owner': 1, 'type': 1, 'tags': 1})
        return entity if entity else None
    except Exception as e:
        return None

def _parse_contact(row: dict) -> Contacts | None:
    if row.get('Contact Name'):
        return Contacts(
            contactName=row.get('Contact Name'),
            position=row.get('Position'),
            emailAddress=row.get('emailAddress'),
            contactLinks=[link.strip() for link in row.get('Contact Network Link', '').split(',')]
        )
    return None

def _parse_department(row: dict) -> Departments | None:
    if row.get('Department Name'):
        return Departments(
            departmentName=row.get('Department Name'),
            departmentLinks=[link.strip() for link in row.get('Department Network Link', '').split(',')]
        )
    return None

def _parse_compliance(row: dict) -> Compliance | None:
    if row.get('Country'):
        return Compliance(
            country=COUNTRIES_MAP.get(row.get('Country', '')),
            localAuthority=row.get('Local Authority'),
            licenseNumber=row.get('License Number'),
            licenseLink=row.get('License Link'),
            registeredName=row.get('Registered Name'),
            dates=parse_date(row.get('Start Date')),
            status=row.get('Lisence status', None),
            licenseType=row.get('License Type')
        )
    return None

def _group_rows_by_entity(reader):

    current_entity_name = None
    current_entity_rows = []

    for row in reader:
        entity_name = row.get('Entity name')
        if not entity_name:
            continue

        if current_entity_name and entity_name != current_entity_name:
            yield current_entity_name, current_entity_rows
            current_entity_rows = []
        
        current_entity_name = entity_name
        current_entity_rows.append(row)
    
    if current_entity_name and current_entity_rows:
        yield current_entity_name, current_entity_rows

def parse_document(reader):
    bearer = get_bearer()
    if not bearer:
        log.error("Could not get bearer token. Aborting upload.")
        return [], [], ["Could not authenticate"], []
        
    common_db = mongo_clients_sync.get('COMMON')
    headers = {
        'Authorization': f'Bearer {bearer}',
        "Content-Type": "application/json"
    }

    created, updated, errors, total = [], [], [], []

    for entity_name, rows in _group_rows_by_entity(reader):
        log.info(f"Processing entity: {entity_name}")
        total.append(entity_name)

        entity = deepcopy(ENTITY_TEMPLATE)

        main_info_row = rows[0] 


        # Main info
        entity['name'] = main_info_row.get('Entity name')
        entity['data']['legalName'] = main_info_row.get('Legal name')
        entity['data']['parentCompany'] = main_info_row.get('Parent company / ownership')
        entity['data']['website'].append(main_info_row.get('Entity website'))
        entity['data']['domicileCountry'] = COUNTRIES_MAP.get(main_info_row.get('Domiciled country'))
        entity['data']['status'] = main_info_row.get('Status').lower()
        entity['type'] = str(TYPES.get(main_info_row.get('Type')))
        entity['tags'] = [str(TAGS.get(name)) for name in main_info_row.get('Tag').split(',')] if main_info_row.get('Tag') else []
        entity['data']['description'] = f'<p>{main_info_row.get("Description")}</p>'
        entity['data']['KYCStatus'] = main_info_row.get('KYC',).strip().replace(' ', '_').lower()
        entity['data']['providedServices'] = [str(SERVICES.get(name.strip())) for name in main_info_row.get('Provided services', '').split(',') if SERVICES.get(name.strip() is not None)] 
        entity['data']['primaryOperationalRegions'] = get_countries(COUNTRIES_MAP, 'Primary operational regions', main_info_row)
        entity['data']['restrictedJurisdictions'] = get_countries(COUNTRIES_MAP, 'Restricted Jurisdictions', main_info_row)
        entity['data']['isFiatCurrencyTrading'] = bool_map.get(main_info_row.get('Fiat currency trading', 'No'))
        entity['data']['officeAddress'] = main_info_row.get('Office address')
        entity['data']['languages'] = [LANGUAGES_MAP.get(name.strip()) for name in main_info_row.get('Languages').split(',')] if main_info_row.get('Languages') else []
        entity['data']['isPrivacyCoinsSupported'] = bool_map.get(main_info_row.get('Privacy coins supported flag', 'No'))
        entity['data']['socialNetworkLinks'] = [link.strip() for link in main_info_row.get('Social network links').split(',')]
        entity['data']['paymentSystems'] = [str(SYSTEMS.get(name.split())) for name in main_info_row.get('Payment systems').split(',')] if main_info_row.get('Payment systems') else []

        # Categories
        entity['data']['contacts'] = [c.__dict__ for row in rows if (c := _parse_contact(row))]
        entity['data']['contactsDepartments'] = [d.__dict__ for row in rows if (d := _parse_department(row))]
        entity['data']['regulatoryCompliance'] = [c.__dict__ for row in rows if (c := _parse_compliance(row))]
        
        try:
            db_entity = find_entity(common_db, entity_name)
            
            if not db_entity:
                stat = create_entity(headers, entity)
                if stat in (200, 201): created.append(entity_name)
                else: errors.append(entity_name)
            else:
                stat = update_entity(str(db_entity['_id']), headers, entity)
                if stat in (200, 201): updated.append(entity_name)
                else: errors.append(entity_name) 
            
            log.info(f"Processed '{entity_name}' with status: {stat}")

        except Exception as e:
            log.error(f"Failed to process entity '{entity_name}': {e}", exc_info=True)
            errors.append(entity_name)

    return created, updated, errors, total