import os
from bson import ObjectId
import logging
from copy import deepcopy
from dataclasses import dataclass, fields
from app.clients import mongo_clients_sync, get_bearer, tags, types, services, systems, languages_map, countries, entity_json, COMMON_ENTITY
from app.utils.parsers import get_countries, parse_date
from app.utils.decorators import exception_retry
from app.models.schemas import Compliance, Contacts, Departments
from app.constants import bool_map
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

def parse_document(reader):
    bearer = get_bearer()
    common_db = mongo_clients_sync.get('COMMON')

    headers = {
        'Authorization': f'Bearer {bearer}',
        "Content-Type": "application/json"
    }

    total = []
    created = []
    updated = []
    errors = []

    contacts = []
    departments = []
    compliances = []
    template = entity_json

    entity = deepcopy(template)
    last_owner = None

    for row in reader:
        owner = row.get('Entity name') 
        if owner and last_owner != owner:
            if last_owner:
                total.append(entity['name'])
                entity['data']['contacts'] = contacts
                entity['data']['contactsDepartments'] = departments
                entity['data']['regulatoryCompliance'] = compliances
                
                db_entity = find_entity(common_db, last_owner)

                if not db_entity:
                    stat = create_entity(headers, entity)
                else:
                    stat = update_entity(str(db_entity['_id']), headers, entity)
                
                if stat in (200, 201):
                    arr = created if stat == 201 else updated
                    arr.append(entity['name'])
                else:
                    errors.append(entity["name"])
                log.info(f"{last_owner}, {stat}")
                    
                entity = deepcopy(template)
                contacts, departments, compliances = [], [], []
            last_owner = owner

            entity['name'] = row.get('Entity name')
            entity['data']['legalName'] = row.get('Legal name')
            entity['data']['parentCompany'] = row.get('Parent company / ownership')
            entity['data']['website'].append(row.get('Entity website'))
            entity['data']['domicileCountry'] = countries.get(row.get('Domiciled country'))
            entity['data']['status'] = row.get('Status').lower()
            entity['type'] = str(types.get(row.get('Type')))
            entity['tags'] = [str(tags.get(name)) for name in row.get('Tag').split(',')] if row.get('Tag') else []
            entity['data']['description'] = f'<p>{row.get("Description")}</p>'
            entity['data']['KYCStatus'] = row.get('KYC',).strip().replace(' ', '_').lower()
            entity['data']['providedServices'] = [str(services.get(name.strip())) for name in row.get('Provided services').split(',') if services.get(name.strip() is not None)] 
            entity['data']['primaryOperationalRegions'] = get_countries(countries, 'Primary operational regions', row)
            entity['data']['restrictedJurisdictions'] = get_countries(countries, 'Restricted Jurisdictions', row)
            entity['data']['isFiatCurrencyTrading'] = bool_map.get(row.get('Fiat currency trading', 'No'))
            entity['data']['officeAddress'] = row.get('Office address')
            entity['data']['languages'] = [languages_map.get(name.strip()) for name in row.get('Languages').split(',')] if row.get('Languages') else []
            entity['data']['isPrivacyCoinsSupported'] = bool_map.get(row.get('Privacy coins supported flag', 'No'))
            entity['data']['socialNetworkLinks'] = [link.strip() for link in row.get('Social network links').split(',')]
            entity['data']['paymentSystems'] = [str(systems.get(name.split())) for name in row.get('Payment systems').split(',')] if row.get('Payment systems') else []

        if row.get('Contact Name'):
            contacts.append(Contacts(
                row.get('Contact Name'),	
                row.get('Position'), 
                row.get('emailAddress'), 
                [link.strip()  for link in row.get('Contact Network Link', '').split(',')]
            ).__dict__)
        
        if row.get('Department Name'):
            departments.append(Departments(
                row.get('Department Name'), 
                [link.strip() for link in row.get('Department Network Link').split(',')]
            ).__dict__)
        
        if row.get('Country'):
            compliances.append(Compliance(
                countries.get(row.get('Country', '')),
                row.get('Local Authority'),
                row.get('License Number'),
                row.get('License Link'),
                row.get('Registered Name'),
                parse_date(row.get('Start Date')),
                row.get('Lisence status', None),
                row.get('License Type')
            ).__dict__)
            
    if last_owner:
        entity['data']['contacts'] = contacts
        entity['data']['contactsDepartments'] = departments
        entity['data']['regulatoryCompliance'] = compliances
        total.append(entity['name'])
        db_entity = find_entity(common_db, last_owner)

        if not db_entity:
            stat = create_entity(headers, entity)
        else:
            stat = update_entity(str(db_entity['_id']), headers, entity)

        if stat in (200, 201):
            arr = created if stat == 201 else updated
            arr.append(entity['name'])
        else:
            errors.append(entity["name"])
        log.info(f"{last_owner}, {stat}")

    return created, updated, errors, total
