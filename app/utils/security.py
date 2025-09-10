
import hmac
import hashlib
import time
import os

def verify_slack_signature(request):
    """
    Check slack signature
    """
    signing_secret = os.environ.get('SLACK_SECRET')
    if not signing_secret:
        print("WARN: SLACK_SECRET не установлен. Проверка подписи пропущена.")
        return True

    timestamp = request.headers.get('X-Slack-Request-Timestamp')
    signature = request.headers.get('X-Slack-Signature')
    
    request_body_bytes = request.get_data()

    if not all([timestamp, signature, request_body_bytes]):
        return False

    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    base_string = f"v0:{timestamp}:".encode('utf-8') + request_body_bytes
    
    my_signature = 'v0=' + hmac.new(
        signing_secret.encode('utf-8'),
        base_string,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(my_signature, signature)