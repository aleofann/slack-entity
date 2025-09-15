import csv
import logging
from datetime import datetime
from app.clients import mongo_clients_sync as dbs
from app.constants import COMMON_ENTITY
from app.data_cache import TAGS, TYPES, BANKS, SYSTEMS_FULL, SERVICES

log = logging.getLogger(__name__)


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
        writer = csv.DictWriter(entity_file, fieldnames=headers)
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
            comp = {row[0]: row[1] for row in enumerate(doc['regulatoryCompliance'])}
            syst = {row[0]: row[1] for row in enumerate(doc['paymentSystems'])}
            banks = {row[0]: row[1] for row in enumerate(doc['banks'])}      
            max_length = max(len(comp), len(syst), len(banks))
            for i in range(0, max_length if max_length else 1):
                parse_data(doc, comp, syst, banks, i, writer, reversed_tags, reversed_types, reversed_services)
        
def parse_data(doc, compliance, systems, banks, index, writer, tags, types, services):
    c_country = compliance.get(index, {}).get('country')
    c_localAuthority = compliance.get(index, {}).get('localAuthority')
    c_licenseNumber = compliance.get(index, {}).get('licenseNumber')
    c_licenseLink = compliance.get(index, {}).get('country')
    c_registeredName = compliance.get(index, {}).get('registeredName')
    c_dates = compliance.get(index, {}).get('dates', {}).get('from', {})
    if c_dates:
        c_dates=datetime.fromtimestamp(int(c_dates)/1000)
    c_status = compliance.get(index, {}).get('status')
    c_licenseType = compliance.get(index, {}).get('licenseType')

    s_systemName = SYSTEMS_FULL.get(systems.get(index), {}).get('systemName')
    s_website = SYSTEMS_FULL.get(systems.get(index), {}).get('website')
    s_paymentTypes = SYSTEMS_FULL.get(systems.get(index), {}).get('paymentTypes')
    s_paymentMethods = SYSTEMS_FULL.get(systems.get(index), {}).get('paymentMethods')
    s_registrationGeography = SYSTEMS_FULL.get(systems.get(index), {}).get('registrationGeography')

    b_bankName = BANKS.get(banks.get(index), {}).get('bankName')
    b_country = BANKS.get(banks.get(index), {}).get('country')
    b_holder = BANKS.get(banks.get(index), {}).get('holder')
    b_accountNumber = BANKS.get(banks.get(index), {}).get('accountNumber')
    b_BIC = BANKS.get(banks.get(index), {}).get('BIC')
    b_IBAN = BANKS.get(banks.get(index), {}).get('IBAN')

    writer.writerow({
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
        # Regulatory Compliance info
        'compliance_country': c_country,
        'compliance_localAuthority': c_localAuthority, 
        'compliance_licenseNumber': c_licenseNumber, 
        'compliance_licenseLink': c_licenseLink, 
        'compliance_registeredName': c_registeredName, 
        'compliance_dates': c_dates,
        'compliance_status': c_status, 
        'compliance_licenseType': c_licenseType, 
        # Payment system info
        'paymentSystems_systemName': s_systemName,
        'paymentSystems_website': s_website,
        'paymentSystems_paymentTypes': s_paymentTypes,
        'paymentSystems_paymentMethods': s_paymentMethods,
        'paymentSystems_registrationGeography': s_registrationGeography,
        # Banks info
        'banks_bankName': b_bankName,
        'banks_country': b_country,
        'banks_holder': b_holder,
        'banks_accountNumber': b_accountNumber,
        'banks_BIC': b_BIC,
        'banks_IBAN': b_IBAN,
        'vision_link': f'https://vision.glprotocol.com/entity-explorer/view/{doc.get("_id")}',
    })