"""
Example WSGI configuration file for PythonAnywhere.
This is what you should put in the WSGI file that PythonAnywhere provides.

IMPORTANT: This is NOT your project's wsgi.py file!
This goes in the WSGI file that PythonAnywhere creates for you in /var/www/
You can find it by clicking the "WSGI configuration file" link in the Web tab.
"""

import sys
import os

# Add your project directory to the path
# Replace 'yourusername' with your PythonAnywhere username
project_home = '/home/yourusername/tiktok_downloader_backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate virtual environment
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

# Import the WSGI application from your project's wsgi.py file
# This will import the 'application' object we created in wsgi.py
from wsgi import application

