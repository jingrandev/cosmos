# gunicorn -c gunicorn.py application.asgi:application
import multiprocessing
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

workers = multiprocessing.cpu_count() * 2 + 1

threads = 1

bind = "0.0.0.0:8080"

daemon = False

worker_class = "uvicorn.workers.UvicornWorker"

worker_connections = 10000

max_requests = 2000
max_requests_jitter = 200

pidfile = "./gunicorn.pid"

loglevel = "info"

preload_app = True

access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

backlog = 512

proc_name = "gunicorn_process"

timeout = 60

graceful_timeout = 60

keepalive = 5

limit_request_line = 5120

limit_request_fields = 101

limit_request_field_size = 8190

accesslog = os.path.join(LOG_DIR, "guni.access.log")
errorlog = os.path.join(LOG_DIR, "guni.error.log")
