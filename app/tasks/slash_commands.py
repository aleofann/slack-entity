import asyncio
import csv
import os
from collections import defaultdict
from app.celery_app import celery
from app.constants import ETH_WALLETS, BTC_WALLETS
from app.utils.owner_search import gather_by_owner
from app.utils.slack_actions import send_message, upload_file
from app.utils.entity_stat import entity_metric
from app.utils.entity_download import export_entities_to_csv

@celery.task(name="get.owner")
def owner_task(owner_name, user_name, thread_ts, channel_id):
    local_filepath = os.path.join("temp_files", f"{user_name}_{thread_ts}.csv")
    
    with open(local_filepath, 'w', encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        data = asyncio.get_event_loop().run_until_complete(gather_by_owner(owner_name))
        for doc in data:
            writer.writerow(doc.values())  

    upload_file(channel_id, local_filepath, user_name, f"{owner_name}_{user_name}")

    if local_filepath and os.path.exists(local_filepath):
        os.remove(local_filepath)

@celery.task(name="entity.stat")
def entity_statystic(channel_id):
    licence_gt1, descr_license, total = entity_metric()
    message_text = (
        f"*Entities with license *: {licence_gt1}\n"
        f"*Entities without license but have description*: {descr_license}\n"
        f"*Total entities*: {total}\n")
    send_message(channel_id, message_text,thread_ts=None)

@celery.task(name="entity.download")
def gather_entity(channel_id, user_name):
    local_filepath = os.path.join("temp_files", f"entities_{user_name}.csv")
    export_entities_to_csv(local_filepath)
    upload_file(channel_id, local_filepath, f"{user_name}_entity", "")
    if local_filepath and os.path.exists(local_filepath):
        os.remove(local_filepath)