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

EVM = ["ETH", "BNB", "TRON", "AVAX"]

CHAINS_MAP = {
    'btc': {'bitcoin', 'xbt', 'btc'},
    'eth': {'ethereum', 'eth'},
    'ltc': {'litecoin', 'ltc'},
    'bnb': {'bsc', 'bnb'},
    'tron': {'trx', 'tron'},
    'bsv': {'bsv'},
    'avax': {'avalanche', 'avax'},
    'arb': {'arbitrum', 'arb'},
    'evm': {'evm'}
}


label_headers = ['address', 'chain']
entity_headers = [
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

bool_map = {
    'Yes': True,
    'No': False
}