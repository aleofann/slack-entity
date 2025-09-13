import asyncio
import csv
from collections import defaultdict
from app.celery_app import celery
from app.constants import ETH_WALLETS, BTC_WALLETS
from app.utils.owner_search import gather_by_owner



@celery.task(name="get.owner")
def owner_task(owner_name: str):
    with open(f"{owner_name}.csv", 'w', encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        data = asyncio.run(gather_by_owner(owner_name))
        for doc in data:
            writer.writerow(doc.values())  

# @celery.task(name="get.labels")
# def label_task(user_name: str, file_id):
#     file_id = event["file_id"]
#     file_info = client.get_file_info(file_id)
#     file_name = file_info["name"]
#     link = file_info["url_private_download"]

#     user_id = file_info['user']
#     user_name = client.get_user_info(user_id)
#     data = asyncio.run(address_labels())