import asyncio
from app.clients import mongo_clients_async as dbs
from app.constants import EVM, BTC_WALLETS, ETH_WALLETS, BTC_CLUSTER

async def fetch_owner(db, collection, owner_name):
    documents = []
    result = db[collection].find({'owner': owner_name}, {'_id': 0, 'address': 1,  'owner': 1})
    async for doc in result:
        documents.append(doc)
    return documents

async def gather_by_owner(owner_name: str):
    tasks = []
    for chain, db in dbs.items():    
        if chain == 'COMMON':
            continue

        collection = ETH_WALLETS
        if chain not in EVM:
            collection = BTC_WALLETS
            tasks.append(fetch_owner(db, BTC_CLUSTER, owner_name))

        tasks.append(fetch_owner(db, collection, owner_name))

    data = await asyncio.gather(*tasks)
    data = [elem for array in data for elem in array]
    return data