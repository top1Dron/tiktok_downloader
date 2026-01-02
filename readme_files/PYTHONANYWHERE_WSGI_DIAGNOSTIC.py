"""
DIAGNOSTIC WSGI file - Use this to find your project path!

This will show you what directories exist and help you find the correct path.
Replace ALL content in PythonAnywhere's WSGI file with this code temporarily.
"""

import os

# Check common locations
home = os.path.expanduser("~")
print(f"Home directory: {home}")

# List contents of home directory
if os.path.exists(home):
    print(f"\nContents of {home}:")
    try:
        items = os.listdir(home)
        for item in items:
            item_path = os.path.join(home, item)
            if os.path.isdir(item_path):
                print(f"  [DIR]  {item}")
                # Check if api_server.py is in this directory
                api_server_path = os.path.join(item_path, "api_server.py")
                if os.path.exists(api_server_path):
                    print(f"         *** FOUND api_server.py here! ***")
                    print(f"         Use this path: {item_path}")
            else:
                print(f"  [FILE] {item}")
    except Exception as e:
        print(f"Error listing directory: {e}")


# Simple response
def application(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-Type", "text/plain")]
    start_response(status, response_headers)
    return [
        b"Check the error log to see directory listing. Look for the path containing api_server.py"
    ]
