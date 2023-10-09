import os

APIKEY = os.environ.get("APIKEY")
if APIKEY is None:
    raise Exception("APIKEY not set")
DEV = os.environ.get("DEV") or False
if DEV:
    print("Running in DEV mode")
CLIENT_URL = os.environ.get("CLIENT_URL") or "http://localhost:3000"



SHOW_DOCS = False
if os.environ.get("SHOW_DOCS") is not None:
    if os.environ.get("SHOW_DOCS").lower() == "true" or os.environ.get("SHOW_DOCS") == "1":
        SHOW_DOCS = True
if DEV:
    SHOW_DOCS = True

