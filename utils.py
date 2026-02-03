import json
import base64


def json_from_base64(base64_bytes):
    return json.loads(base64.b64decode(base64_bytes).decode("utf-8"))
