"""
WSGI entry point for PythonAnywhere deployment.
Wraps the FastAPI ASGI application in a WSGI adapter.
"""

from asgiref.wsgi import WsgiToAsgi
from api_server import app

# Wrap FastAPI (ASGI) app in WSGI adapter for PythonAnywhere
application = WsgiToAsgi(app)
