import os
import csv
import requests
import asyncio
from app.celery_app import celery
from app.clients import slack_clients
from app.utils.slack_actions import send_message, get_file_info, get_user_info, upload_file
from app.utils.address_labels import fetch_labels
from app.utils.entity_upload import parse_document
from app.constants import label_headers, entity_headers


slack_client = slack_clients.get("MAIN")

@celery.task(name="process.file")
def process_file(file_id: str, channel_id: str, user_id: str):

    try:
        
        file_info = get_file_info(slack_client, file_id)
        user_name = get_user_info(slack_client, user_id)

        thread_ts = file_info.get('shares', {}).get('private', {}).get(channel_id, [{}])[0].get('ts', None)

        if file_info.get('filetype') != 'csv':
            send_message(channel_id, "The file must be in CSV format.", thread_ts)
            return

        os.makedirs("temp_files", exist_ok=True)
        local_filepath = os.path.join("temp_files", f"{user_name}_{thread_ts}.csv")
        print(local_filepath)
        
        response = requests.get(
            file_info['url_private_download'],
            headers={'Authorization': f'Bearer {slack_client.token}'}
        )
        response.raise_for_status()

        file_data = response.content.decode('utf-8')
        reader = csv.DictReader(file_data.splitlines())
        
        reader_headers = {row.strip().lower() for row in reader.fieldnames}
        label_template = {row.strip().lower() for row in label_headers}
        entity_template = {row.strip().lower() for row in entity_headers}


        if label_template.issubset(reader_headers):
            send_message(channel_id, 'Got a file for labels', thread_ts)
            
            # asyncio.run(fetch_labels(local_filepath, reader))
            # upload_file(channel_id,local_filepath, user_name, 'comment', thread_ts)
        elif entity_template.issubset(reader_headers):
            created, updated, errors, total = parse_document(reader)
            message_text = (
                f":heavy_plus_sign: *Created*: {len(created)}\n"
                f":white_check_mark: *Updated*: {len(updated)}\n"
                f":warning: *Errors*: {len(errors)}\n"
                f"*Uploaded by {user_name}*")
            
            send_message(channel_id, message_text, thread_ts)
            


        # os.remove(local_filepath)
        # # 3. Запускаем тяжелую обработку (как мы делали раньше)
        # output_filepath = f"results_{file_info['name']}"
        # success = asyncio.run(enrich_addresses_from_file(local_filepath, output_filepath))

        # if success:
        #     upload_file(channel_id, output_filepath, "Результаты обработки", "Готово!", thread_ts)
        # else:
        #     send_message(channel_id, "Не удалось найти данные для обработки в файле.", thread_ts)

    except Exception as e:
        send_message(channel_id, f"Произошла критическая ошибка: {e}", thread_ts)
        
