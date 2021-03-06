# gunicorn config
# gunicorn -c config/gunicorn.py --worker-class sanic.worker.GunicornWorker server:app
import os

os.environ['MODE'] = 'PRO'

WORKERS = os.getenv('WORKERS', 4)
TIMEOUT = os.getenv('TIMEOUT', 20)

bind = '0.0.0.0:8000'
backlog = 2048

workers = WORKERS
worker_connections = 1000
keepalive = 2

spew = False
daemon = False

umask = 0
timeout = TIMEOUT
preload = True
reload = False
