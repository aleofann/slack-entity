from flask import Blueprint, request, jsonify
from app.clients import mongo_clients_async as dbs
from app.tasks.reports import owner_task

slack_bp = Blueprint("slack", __name__, url_prefix="/slack")
events_bp = Blueprint("events", __name__, url_prefix="/events")

@slack_bp.route("/owner", methods=["POST"])
def test_owner():
    owner_name = request.form.get('text').strip()
    task = owner_task.delay(owner_name)
    return jsonify({
        "status": "Submited",
        'task_id': "task.id"
    }), 202

@events_bp.route('/', methods=["POST"])
def test_event():
    
    request_data = request.json
    print(request)
    if "challenge" in request_data:
        return jsonify({"challenge": request_data["challenge"]}), 200
    
    # if not signature.is_valid_request(request.get_data(), request.headers):
    #     return make_response("Invalid request", 403)
    return jsonify({"status": "ok"}), 200

# celery -A celery_app.celery_app worker -l info -Q debug_queue -P solo --concurrency=2