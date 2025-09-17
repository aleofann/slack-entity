import asyncio
import csv
import os
from copy import deepcopy
from collections import defaultdict
from app.clients import mongo_clients_async as dbs
from app.constants import EVM, BTC_WALLETS, ETH_WALLETS, ETH_TRANSACTIONS, CHAIN_MAP, USDT, ADDRESS_INFO_TEMPLATE, WRITER_LABEL_HEADER
from app.data_cache import BTC_PIPELINE, ETH_PIPELINE, TAGS, TYPES
import logging


os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("my_module_logger")
logger.setLevel(logging.DEBUG)
logger.propagate = False

file_handler = logging.FileHandler("logs/my_module.log")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

semaphore = asyncio.BoundedSemaphore(45)

reversed_tags = {v:k for k,v in TAGS.items()}
reversed_types = {v:k for k,v in TYPES.items()}

def read_file(reader):
    reader.fieldnames = [row.casefold() for row in reader.fieldnames]
    addresses = defaultdict(list)

    for row in reader:
        address = row["address"]
        chain = row["chain"]
        default_chain = ""

        for chain_name, variants in CHAIN_MAP.items():
            if chain.casefold() in variants:
                default_chain = chain_name
                break
        
        if default_chain:
            addresses[default_chain].append(address)
    return addresses

async def usdt_count(client, address, token):
    query_from = {"from": address.strip(), "address": token, "value": {"$gt": 0}}
    query_to = {"to": address.strip(), "address": token, "value": {"$gt": 0}}
    count_from_task = client[ETH_TRANSACTIONS].count_documents(query_from, hint="from1_address1_value1")
    count_to_task = client[ETH_TRANSACTIONS].count_documents(query_to, hint="to1_address1_value1")
    total_from, total_to = await asyncio.gather(count_from_task, count_to_task)
    return total_from + total_to

async def fetch_address(client, collection, address, chain):
    async with semaphore:
        try:
            pipe = deepcopy(ETH_PIPELINE if chain in EVM else BTC_PIPELINE)
            pipe[0]["$match"]["address"] = address

            result = await client[collection].aggregate(pipe, maxTimeMS=60000).to_list(None)
            
            if not result:
                empty_template = deepcopy(ADDRESS_INFO_TEMPLATE)
                empty_template[0].update({"address": address, "chain": chain, "usdt_txCount": "", "txCount": ""})
                return empty_template
            
            adr_tags = [reversed_tags.get(row, "") for row in result[0]["adr_tag"]]
            adr_type = reversed_types.get(result[0]["adr_type"])
            c_tags = [reversed_tags.get(row, "") for row in result[0]["c_tag"]]
            c_type = reversed_types.get(result[0]["c_type"])
            result[0].update({"adr_tag": adr_tags, "adr_type": adr_type, "c_tag": c_tags, "c_type": c_type, "chain": chain})

            if chain in EVM:
                tasks = [usdt_count(client, address, USDT[chain]), usdt_count(client, address, None)]
                usdt_total, native_total = await asyncio.gather(*tasks)
                result[0].update({"usdt_txCount": usdt_total, "txCount": native_total})

            return result
        except Exception as e:
            logger.info("Attempting to gather labels")
            return e


async def fetch_all(client, collection, addresses, chain):
    tasks = []
    for address in addresses:
        tasks.append(asyncio.create_task(fetch_address(client, collection, address, chain)))

    data = await asyncio.gather(*tasks)
    return data

async def gather_labels(filepath, reader):
    try:
        logger.info("Attempting to gather labels")
        address_map = read_file(reader)

        tasks = []
        for chain, addresses in address_map.items():
            client = dbs.get(chain)
            collection = BTC_WALLETS

            if chain in EVM:
                collection = ETH_WALLETS
            tasks.append(asyncio.create_task(fetch_all(client, collection, addresses, chain)))

        # print(address_map.items())
        print('starting gathering')
        data = await asyncio.gather(*tasks)
        print('finished gathering')
        
        with open(filepath, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=WRITER_LABEL_HEADER, extrasaction="ignore") 
            writer.writeheader()

            for array in data:
                for elem in array:
                    writer.writerow(elem[0])
            return 200
    except Exception as e:
        print(e)
        logger.info(e)
        return e