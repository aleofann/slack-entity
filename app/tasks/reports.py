import asyncio
from app.celery_app import celery
from app.constants import ETH_WALLETS, BTC_WALLETS
from app.utils.owner_search import gather_by_owner
import csv


@celery.task(name="get.owner")
def owner_task(owner_name: str):
    print(owner_name)
    with open(f"{owner_name}.csv", 'w', encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        data = asyncio.run(gather_by_owner(owner_name))
        for doc in data:
            writer.writerow(doc.values())  