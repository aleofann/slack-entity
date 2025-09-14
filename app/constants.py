# General collections
ETH_WALLETS = "eth_wallets"
ETH_TRANSACTIONS = "eth_transactions"
BTC_WALLETS = "_wallets"
BTC_TRANSACTIONS = "_txs"
BTC_CLUSTER = "_clusters"

# Common label 
COMMON_LABEL = "label"
COMMON_TAGS = "tag"
COMMON_TYPES = "type"

# Common entity
COMMON_ENTITY = "entity"
COMMON_PAYMENT_METHOD = "payment_method"
COMMON_PAYMENT_SYSTEM = "payment_system"
COMMON_SERVICE = "provided_service"
COMMON_BANKS = "banks"

EVM = ["ETH", "BNB", "TRON", "AVAX", "ARB"]

CHAIN_MAP = {
    'BTC': {'bitcoin', 'xbt', 'btc'},
    'ETH': {'ethereum', 'eth'},
    'LTC': {'litecoin', 'ltc'},
    'BNB': {'bsc', 'bnb'},
    'TRON': {'trx', 'tron'},
    'BSV': {'bsv'},
    'AVAX': {'avalanche', 'avax'},
    'ARB': {'arbitrum', 'arb'},
    'EVM': {'evm'}
}

USDT = {
    'ETH': '0xdAC17F958D2ee523a2206206994597C13D831ec7'.casefold(),
    'TRON': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
    'BNB': '0x55d398326f99059ff775485246999027b3197955'.casefold(),
    'AVAX': '0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7'.casefold(),
    'ARB': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'.casefold()
}

WRITER_LABEL_HEADER = [
    'address','owner','description','adr_tag','adr_type','cluster',
    'c_owner','c_descr','c_type','c_tag','count_adr','contract',
    'avax_isContract','arb_isContract','bnb_isContract','txCount',
    'usdt_txCount','avax_usdt_txCount', 'avax_txCount', 'arb_usdt_txCount',
    'arb_txCount','bnb_usdt_txCount','bnb_txCount', 'tags_meta','chain'
    ]

ADDRESS_INFO_TEMPLATE = [
        {
        'address': '', 'owner': '', 'description': '', 'adr_tag': '', 
        'adr_type': '', 'cluster': '', 'c_owner': '', 'c_descr': '', 
        'c_type': '', 'c_tag': '', 'count_adr': '', 'contract': '', 
        'txCount': '', 'usdt_txCount': '', 'tags_meta': '', 'chain': ''
    }
    ]

READER_LABEL_HEADER = ['address', 'chain']
READER_ENTITY_HEADERS = [
    # Main info
    'entity name', 
    'legal name', 
    'parent company / ownership', 
    'entity website', 
    'domiciled country', 
    'status',
    'type', 
    'tag', 
    'description', 
    'kyc', 
    'provided services', 
    'primary operational regions', 
    'restricted jurisdictions',
    'fiat currency trading', 
    'office address', 
    'languages', 
    'privacy coins supported flag', 
    'social network links',
    'payment systems', 
    # Licences
    'country', 
    'local authority', 
    'license number', 
    'license type', 
    'license link', 
    'registered name',
    'start date', 
    # Contacts
    'contact name', 
    'position', 
    'contact network link', 
    # Departments
    'department name', 
    'department network link']

BOOL_MAP = {
    'Yes': True,
    'No': False
}