import os

APIKEY = os.environ.get("APIKEY")
if APIKEY is None:
    raise Exception("APIKEY not set")
DEV = os.environ.get("DEV") or False
if DEV:
    print("Running in DEV mode")
CLIENT_URL = os.environ.get("CLIENT_URL") or "http://localhost:3000"

MONGODB_CONNECTION_URI = os.environ.get("MONGODB_CONNECTION_URI") or "mongodb://admin:admin@127.0.0.1:27017/jobs_db_dev?authSource=admin"
DB_NAME = os.environ.get("DB_NAME") or "jobs_db_dev"
COLL_NAME = os.environ.get("COLL_NAME") or "job_results"

SHOW_DOCS = False
if os.environ.get("SHOW_DOCS") is not None:
    if os.environ.get("SHOW_DOCS").lower() == "true" or os.environ.get("SHOW_DOCS") == "1":
        SHOW_DOCS = True
if DEV:
    SHOW_DOCS = True

