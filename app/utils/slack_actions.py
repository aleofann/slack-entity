
import os
from app.clients import slack_clients
from slack_sdk.errors import SlackApiError


slack_client = slack_clients.get("MAIN")

def send_message(channel_id: str, text: str, thread_ts: str = None):
    if not slack_client:
        print("WARN: Slack client not configured. Message not sent.")
        return
    print(thread_ts)
    try:
        slack_client.chat_postMessage(
            channel=channel_id,
            text=text,
            thread_ts=thread_ts
        )
    except Exception as e:
        print(f"Error sending Slack message to {channel_id}: {e}")

def upload_file(channel_id: str, filepath: str, title: str, initial_comment: str, thread_ts: str = None):
    if not slack_client or not os.path.exists(filepath):
        print(f"WARN: Slack client not configured or file {filepath} not found. File not uploaded.")
        return
    try:
        slack_client.files_upload_v2(
            channel=channel_id,
            file=filepath,
            title=title,
            initial_comment=initial_comment,
            thread_ts=thread_ts
        )
    except Exception as e:
        print(f"Error uploading file {filepath} to Slack: {e}")

def get_user_info(client, user_id: str):
    try:
        response = client.users_info(user=user_id)
        return response['user']['name']
    except SlackApiError as e:
        print(f"Slack user info failed: {e.response['error']}")
        return None
    
def get_file_info(client, file_id: str):
    try:
        response = client.files_info(file=file_id)
        return response['file']
    except SlackApiError as e:
        print(f"Slack file info failed: {e.response['error']}")
        return None