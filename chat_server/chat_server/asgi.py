# daphne -b 0.0.0.0 -p 8080 chat_server.asgi:application

import os
import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_server.settings")
django.setup()
application = get_default_application()
