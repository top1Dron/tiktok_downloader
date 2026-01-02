"""
WSGI entry point for PythonAnywhere deployment.
Uses Flask app which is native WSGI (no adapter needed).
"""

import os
import sys

# Set working directory to the project directory
# This helps load_dotenv() find the .env file
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)
sys.path.insert(0, project_dir)

from api_server_flask import app

# Flask app is already WSGI-compatible
application = app
