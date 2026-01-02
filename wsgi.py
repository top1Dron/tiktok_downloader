"""
WSGI entry point for PythonAnywhere deployment.
Uses Flask app which is native WSGI (no adapter needed).
"""

from api_server_flask import app

# Flask app is already WSGI-compatible
application = app
