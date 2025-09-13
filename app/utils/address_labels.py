import asyncio
import csv
# from app.clients import mongo_clients_async as dbs
# from app.constants import EVM, BTC_WALLETS, ETH_WALLETS

async def fetch_labels(filepath,reader):
    file = open(filepath, 'w', encoding='utf-8', newline='')
    writer = csv.writer(file)
    for row in reader:
        writer.writerow(row.values())
    file.flush()
    
#     reader.fieldnames = [row.casefold() for row in self.reader.fieldnames]

#     addresses = defaultdict(list)

#     for row in self.reader:
#         address = row['address']
#         chain = row['chain']
#         default_chain = ''

#         for chain_name, variants in self.chains.items():
#             if chain.casefold() in variants:
#                 default_chain = chain_name
#                 break
        
#         if default_chain:
#             addresses[default_chain].append(address)