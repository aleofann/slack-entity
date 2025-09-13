from flask import Blueprint, request, jsonify, make_response, current_app
from app.clients import mongo_clients_async, slack_clients
from app.tasks.reports import owner_task
from app.tasks.file_tasks import process_file
from app.utils.security import verify_slack_signature


slack_bp = Blueprint("slack", __name__, url_prefix="/slack")
events_bp = Blueprint("events", __name__, url_prefix="/events")

@slack_bp.route("/owner", methods=["POST"])
def get_owner():
    owner_name = request.form.get('text')
    if not owner_name:
        return jsonify({
        "response_type": "ephemeral",
        "text": (
            ":warning:*Entity name can't be empty*\n"
            "\nExample: /owner Binance"
        )
    }), 200

    task = owner_task.delay(owner_name.strip())
    return jsonify({
        "response_type": "ephemeral",
        "text": f"Gathering addresses of {owner_name}"
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

@events_bp.route('/', methods=["POST"])
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

        if event.get('channel_id') != current_app.config.get('SLACK_CHANNEL'):
            return make_response("", 200)

        if event.get("type") == "file_shared":
            user_id = event.get("user_id")
            file_id = event.get("file_id")

            if user_id == 'U076B5REWM9':
                return jsonify({"status": "ok"}), 200
    
            process_file.delay(file_id, current_app.config.get('SLACK_CHANNEL'), user_id)

    return jsonify({"status": "ok"}), 200

# celery -A celery_app.celery_app worker -l info -Q debug_queue -P solo --concurrency=2