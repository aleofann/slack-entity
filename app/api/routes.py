import os
import time
from flask import Blueprint, request, jsonify, make_response, current_app
from app.clients import mongo_clients_async, slack_clients
from app.tasks.slash_commands import owner_task, entity_statystic, gather_entity
from app.tasks.file_tasks import process_file
from app.utils.security import verify_slack_signature


slack_bp = Blueprint("slack", __name__, url_prefix="/slack")
events_bp = Blueprint("events", __name__, url_prefix="/events")
entity_bp = Blueprint("entity", __name__, url_prefix="/entities")

@entity_bp.route("/collect-entities", methods=["POST"])
def collect_entities():
    user_name = request.form.get("user_name")
    channel = current_app.config.get("SLACK_CHANNEL")
    task = gather_entity.delay(channel, user_name)
    return jsonify({
        "response_type": "ephemeral",
        "text": f"Gathering entities"
    }), 202

@entity_bp.route("/entity-stat", methods=["POST"])
def entity_stat():
    user_name = request.form.get("user_name")
    ts = int(time.time())
    channel = current_app.config.get("SLACK_CHANNEL")
    task = entity_statystic.delay(channel)
    print(task)
    print(task.__dict__)
    return jsonify({
        "response_type": "ephemeral",
        "text": f"Gathering stat"
    }), 202

@slack_bp.route("/owner", methods=["POST"])
def get_owner():
    db_owner_name = request.form.get("text")
    
    if not db_owner_name:
        return jsonify({
        "response_type": "ephemeral",
        "text": (
            ":warning:*Entity name can't be empty*\n"
            "\nExample: /owner Binance"
        )
    }), 200

    user_name = request.form.get("user_name")
    ts = int(time.time())

    task = owner_task.delay(db_owner_name.strip(), user_name, ts, current_app.config.get("SLACK_CHANNEL"))
    return jsonify({
        "response_type": "ephemeral",
        "text": f"Gathering {db_owner_name} addresses"
    }), 202

@slack_bp.route("/info", methods=["POST"])
def info():
    return jsonify({
        "response_type": "ephemeral",
        "text": (
            ":warning:*List of commands*\n"
            "\n:one: /owner "
            "\nExample: /owner Binance"
            
        )
    }), 200

@events_bp.route("/", methods=["POST"])
def slack_event():
    
    request_data = request.json
    if "challenge" in request_data:
        return jsonify({"challenge": request_data["challenge"]}), 200
    
    if not verify_slack_signature(request):
        return make_response("Invalid request signature", 403)
    
    if "X-Slack-Retry-Num" in request.headers:
        return make_response("", 200)
    
    if "event" in request_data:
        event = request_data["event"]

        if event.get("channel_id") != current_app.config.get("SLACK_CHANNEL"):
            return make_response("", 200)

        if event.get("type") == "file_shared":
            user_id = event.get("user_id")
            file_id = event.get("file_id")
            # print(event)
            # print(event.get("user_id"))
            if user_id == os.environ.get("SLACK_BOT_ID"):
                return jsonify({"status": "ok"}), 200
    
            process_file.delay(file_id, current_app.config.get("SLACK_CHANNEL"), user_id)

    return jsonify({"status": "ok"}), 200

