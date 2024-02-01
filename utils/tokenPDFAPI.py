import os
import hmac
import json
import base64
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY_PDF = os.getenv("API_KEY_PDF")
API_SECRET_PDF = os.getenv("API_SECRET_PDF")
USER_REQUEST_PDF = os.getenv("USER_REQUEST_PDF")


def hmac_sha256(message, key):
    return hmac.new(key.encode("utf-8"), message.encode("utf-8"), "sha256").digest()


def encode_to_base64(data):
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


def create_message(header, payload):
    header_string = encode_to_base64(json.dumps(header))
    payload_string = encode_to_base64(json.dumps(payload))
    return f"{header_string}.{payload_string}"


def to_timestamp_unix(time):
    return int(time.timestamp())


def timestamp_hours(date):
    time = date + timedelta(hours=1)
    return to_timestamp_unix(time)


def signature_token(epoch):
    header = {
        "alg": "HS256",
        "typ": "JWT",
    }

    payload = {
        "iss": API_KEY_PDF,
        "sub": USER_REQUEST_PDF,
        "exp": epoch,
    }

    message = create_message(header, payload)
    signature = base64.b64encode(hmac_sha256(message, API_SECRET_PDF)).decode("utf-8")
    return f"{message}.{signature}"


def generate_jwt_token():
    moment_save = datetime.utcnow()
    epoch_timestamp = timestamp_hours(moment_save)
    bearer_token = signature_token(epoch_timestamp)

    return bearer_token