import os

bind = '0.0.0.0:8000'
workers = int(os.environ.get('WEB_CONCURRENCY', '2'))
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '180'))
accesslog = '-'
errorlog = '-'
capture_output = True
# Web is only reachable on the private Compose network.
forwarded_allow_ips = '*'
