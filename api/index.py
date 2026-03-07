"""
Vercel serverless function entry point
Wraps the FastAPI app with Mangum for AWS Lambda compatibility
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mangum import Mangum

# Diagnostic fallback app
_diag_app = FastAPI()
_import_errors = {}

@_diag_app.get("/api/diagnostic")
def diagnostic():
    return {"status": "import_failed", "errors": _import_errors}

@_diag_app.api_route("/{path:path}", methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS"])
def fallback(path: str):
    return JSONResponse({"error": "App failed to import", "details": _import_errors}, status_code=503)

# Try to import real app
try:
    from api_main_gdpr import app
    handler = Mangum(app, lifespan="off")
except Exception as e:
    import traceback
    _import_errors["api_main_gdpr"] = str(e)
    _import_errors["traceback"] = traceback.format_exc()
    handler = Mangum(_diag_app, lifespan="off")
