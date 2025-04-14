# api/server.py
import os
from django.core.wsgi import get_wsgi_application

# If you want to use serverless-wsgi, import it:
# from serverless_wsgi import handle_request

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz_backend.settings')
application = get_wsgi_application()

# If using serverless-wsgi, define a handler like so:
# def handler(event, context):
#     return handle_request(application, event, context)
