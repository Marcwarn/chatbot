"""
Diagnostic wrapper - returns actual import error
"""
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mangum import Mangum
    from api_main_gdpr import app
    handler = Mangum(app, lifespan="off")
except Exception as e:
    import json
    from mangum import Mangum

    async def error_app(scope, receive, send):
        if scope["type"] == "http":
            body = json.dumps({
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }).encode()
            await send({"type": "http.response.start", "status": 500,
                        "headers": [[b"content-type", b"application/json"]]})
            await send({"type": "http.response.body", "body": body})

    handler = Mangum(error_app, lifespan="off")
