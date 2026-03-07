"""
Vercel serverless function entry point
Wraps the FastAPI app with Mangum for AWS Lambda compatibility
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mangum import Mangum
from api_main_gdpr import app

handler = Mangum(app, lifespan="off")
