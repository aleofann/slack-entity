import csv
import logging
from datetime import datetime
from app.clients import mongo_clients_sync as dbs
from app.constants import COMMON_ENTITY
from app.data_cache import TAGS, TYPES, BANKS, SYSTEMS_FULL, SERVICES

log = logging.getLogger(__name__)

def parse_main_info(doc, tags, types, services):
    return {
    'name': doc.get('name'),
    'owner': doc.get('owner'),
    'legalName': doc.get('legalName'),
    'type': types.get(doc.get('type')),
    'tags': [tags.get(row) for row in doc.get('tags') if row] if doc.get('tags') else [],
    'isActive': doc.get('isActive'),
    'KYCStatus': doc.get('KYCStatus'),
    'isFiatCurrencyTrading': doc.get('isFiatCurrencyTrading'),
    'isPrivacyCoinsSupported': doc.get('isPrivacyCoinsSupported'),
    'website': doc.get('website'),
    'parentCompany': doc.get('isFiatCurrencyTrading'),
    'domicileCountry': doc.get('domicileCountry'),
    'status': doc.get('status'),
    'description': doc.get('description'),
    'officeAddress': doc.get('officeAddress'),
    'providedServices': [services.get(row) for row in doc.get('providedServices')],
    'primaryOperationalRegions': doc.get('primaryOperationalRegions'),
    'restrictedJurisdictions': doc.get('restrictedJurisdictions'),
    'languages': doc.get('languages'),
    'socialNetworkLinks': doc.get('socialNetworkLinks'),
    }

def export_entities_to_csv(filepath: str = 'entities.csv'):
    
    log.info(f"Starting entity export to {filepath}...")

    reversed_tags = {v: k for k, v in TAGS.items()}
    reversed_types = {v: k for k, v in TYPES.items()}
    reversed_services = {v: k for k, v in SERVICES.items()}

    headers = [
        'name','owner','legalName','type','tags','isActive','KYCStatus','isFiatCurrencyTrading',
        'isPrivacyCoinsSupported','website','parentCompany','domicileCountry','status','description',
        'officeAddress','providedServices','primaryOperationalRegions','restrictedJurisdictions',
        'languages','socialNetworkLinks','compliance_country','compliance_localAuthority',
        'compliance_licenseNumber','compliance_licenseLink','compliance_registeredName',
        'compliance_dates','compliance_status','compliance_licenseType','paymentSystems_systemName',
        'paymentSystems_website','paymentSystems_paymentTypes','paymentSystems_paymentMethods',
        'paymentSystems_registrationGeography','banks_bankName','banks_country','banks_holder',
        'banks_accountNumber','banks_BIC','banks_IBAN','vision_link', 'has_wallet'
    ]

    
    with open(filepath, 'w', encoding='utf-8', newline='') as entity_file:
        writer = csv.DictWriter(entity_file, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        
        common_db_client = dbs.get("COMMON")
        if not common_db_client:
            log.error("COMMON database client not found.")
            return None
        
        collection = common_db_client[COMMON_ENTITY][COMMON_ENTITY]

        cursor = collection.find({}, {
            '_id': 1,
            'legalName': '$data.legalName',
            'name': 1,
            'owner': 1,
            'type': 1,
            'tags': 1,
            'isActive': '$data.isActive',
            'KYCStatus': '$data.KYCStatus',
            'isFiatCurrencyTrading': '$data.isFiatCurrencyTrading',
            'isPrivacyCoinsSupported': '$data.isPrivacyCoinsSupported',
            'website': '$data.website',
            'parentCompany': '$data.parentCompany',
            'domicileCountry': '$data.domicileCountry',
            'status': '$data.status',
            'description': '$data.description',
            'officeAddress': '$data.officeAddress',
            'providedServices': '$data.providedServices',
            'primaryOperationalRegions': '$data.primaryOperationalRegions',
            'restrictedJurisdictions': '$data.restrictedJurisdictions',
            'languages': '$data.languages',
            'socialNetworkLinks': '$data.socialNetworkLinks',
            'regulatoryCompliance': '$data.regulatoryCompliance',
            'banks': '$data.banks',
            'paymentSystems': '$data.paymentSystems',
            'contacts': '$data.contacts',
            'contactsDepartments': '$data.contactsDepartments',
        })

        for doc in cursor:
            main_info = parse_main_info(doc, reversed_tags, reversed_types, reversed_services)
            compliances = {row[0]: row[1] for row in enumerate(doc['regulatoryCompliance'])}
            systems_ids = {row[0]: row[1] for row in enumerate(doc['paymentSystems'])}
            banks_ids = {row[0]: row[1] for row in enumerate(doc['banks'])}

            if not any([compliances, systems_ids, banks_ids]):
                writer.writerow(main_info)    
                continue  

            max_len = max(len(compliances), len(systems_ids), len(banks_ids))
            for i in range(max_len):
                info = main_info.copy()

                if i < len(compliances):
                    comp = compliances[i]
                    date_from = comp.get('dates', {}).get('from')
                    info.update({
                        'compliance_country': comp.get('country'),
                        'compliance_localAuthority': comp.get('localAuthority'),
                        'compliance_licenseNumber': comp.get('licenseNumber'),
                        'compliance_licenseLink': comp.get('licenseLink'),
                        'compliance_registeredName': comp.get('registeredName'),
                        'compliance_dates': datetime.fromtimestamp(int(date_from) / 1000).strftime('%Y-%m-%d') if date_from else '',
                        'compliance_status': comp.get('status'),
                        'compliance_licenseType': comp.get('licenseType'),
                    })

                if i < len(systems_ids):
                    system_obj = SYSTEMS_FULL.get(systems_ids[i])
                    if system_obj:
                        info.update({
                            'paymentSystems_systemName': system_obj.get('systemName'),
                            'paymentSystems_website': system_obj.get('website'),
                            'paymentSystems_paymentTypes': ", ".join(system_obj.get('paymentTypes') or []),
                            'paymentSystems_paymentMethods': ", ".join(system_obj.get('paymentMethods') or []),
                            'paymentSystems_registrationGeography': system_obj.get('registrationGeography'),
                        })

                if i < len(banks_ids):
                    bank_obj = BANKS.get(banks_ids[i])
                    if bank_obj:
                        info.update({
                            'banks_bankName': bank_obj.get('bankName'),
                            'banks_country': bank_obj.get('country'),
                            'banks_holder': bank_obj.get('holder'),
                            'banks_accountNumber': bank_obj.get('accountNumber'),
                            'banks_BIC': bank_obj.get('BIC'),
                            'banks_IBAN': bank_obj.get('IBAN'),
                        })
                writer.writerow(info)
                    