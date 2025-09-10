import asyncio
from app.clients import mongo_clients_async as dbs
from app.constants import EVM, BTC_WALLETS, ETH_WALLETS

async def fetch_owner(db, collection, owner_name: str, ):
    documents = []

    result = db[collection].find({
        'owner': owner_name  
    }, {'_id': 0, 'address': 1,  'owner': 1})

    async for doc in result:
        documents.append(doc)

    return documents

async def gather_by_owner(owner_name: str):
    tasks = []
    owner = owner_name.strip()
    for chain, db in dbs.items():    
        if chain == 'COMMON':
            continue

        collection = BTC_WALLETS
        if chain in EVM:
            collection = ETH_WALLETS
        tasks.append(fetch_owner(db, collection, owner_name))

    data = await asyncio.gather(*tasks)
    data = [elem for array in data for elem in array]
    return data