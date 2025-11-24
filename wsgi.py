"""WSGI Entry Point for Rwanda Climate Alerts

This module serves as the WSGI (Web Server Gateway Interface) entry point
for deploying the Flask application with production servers like Gunicorn or uWSGI.

Usage:
    gunicorn wsgi:app
"""

from app import app

# --------------------------- For Testing Locally ---------------------------
# if __name__ == "__main__":
#     app.run()