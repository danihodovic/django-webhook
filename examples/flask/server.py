import hmac
from hashlib import sha256

from flask import Flask, Response, request

app = Flask(__name__)

webhook_secret = "very-secret-token"


@app.route("/webhook", methods=["POST"])
def webhook():
    signatures_str = request.headers.get("Django-Webhook-Signature-v1", "")
    signatures = signatures_str.split(",")
    timestamp = request.headers["Django-Webhook-Request-Timestamp"]

    for signature in signatures:
        digest_payload = bytes(timestamp, "utf8") + b":" + request.data
        digest = hmac.new(
            key=webhook_secret.encode(),
            msg=digest_payload,
            digestmod=sha256,
        )
        signature_valid = hmac.compare_digest(digest.hexdigest(), signature)
        if not signature_valid:
            app.logger.warning("Invalid signature from incoming webhook")
            return Response("Invalid signature", status=400)

    app.logger.info(request.json)
    return Response("Webhook received.", status=200)
