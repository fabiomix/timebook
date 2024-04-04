# Gunicorn configuration file
wsgi_app = "wsgi:app"

# Logging
accesslog = "-"
errorlog = "-"

# Server Socket
bind = "0.0.0.0:8000"

# Worker Processes
workers = 2
max_requests = 600
timeout = 30
