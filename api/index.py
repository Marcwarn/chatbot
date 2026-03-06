"""
Vercel serverless function entry point
Wraps the FastAPI app with Mangum for AWS Lambda compatibility
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from mangum import Mangum
from api_main_gdpr import app

# Wrap FastAPI app with Mangum for serverless deployment
handler = Mangum(app, lifespan="off")
