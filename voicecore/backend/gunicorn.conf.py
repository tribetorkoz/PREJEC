import multiprocessing
import os

# VoiceCore - Enterprise Gunicorn Configuration for Scaling FastAPI

# Bind the server to the internal Docker/Network Host
bind = "0.0.0.0:8000"

# Auto-calculate the maximum optimal number of worker processes
# based on the physical processing cores of the server CPU.
# Formula: (2 x $num_cores) + 1
workers_per_core_str = os.getenv("WORKERS_PER_CORE", "2")
cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores + 1
web_concurrency = int(os.getenv("WEB_CONCURRENCY", str(default_web_concurrency)))

# Max Web Concurrency Limit
workers = max(web_concurrency, 2)

# Use Uvicorn's incredibly fast async worker class
worker_class = "uvicorn.workers.UvicornWorker"

# Graceful Timeouts (Drop hanging requests to protect CPU cycles)
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))

# Logging format matching Structlog expectations
loglevel = os.getenv("LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"
