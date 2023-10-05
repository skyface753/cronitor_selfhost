from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from uvicorn.config import LOGGING_CONFIG





import server.config.config as config
    
    
docs_url = "/api/v1/docs" if config.SHOW_DOCS else None
redoc_url = "/api/v1/redocs" if config.SHOW_DOCS else None
app = FastAPI(
    title="Cronitor Selfhost API",
    docs_url=docs_url,
    redoc_url=redoc_url,
)

origins = [
    config.CLIENT_URL,
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


from pymongo import MongoClient
@app.on_event("startup")
def startup_db_client():
    if config.DEV:
        # Clear the database
        client = MongoClient(config.MONGODB_CONNECTION_URI)

        client.drop_database(config.DB_NAME)
        # Insert some test data
        for job in config.jobs:
            client[config.DB_NAME][config.COLL_NAME].insert_one({"job_id": job["id"], "success": False, "message": "ÄLTESTER", "timestamp": "2021-01-01T00:00:00.000Z", "command": "notARealCommand 'Hallo Welt'", "runtime": 2.0})
        for i in range(10):
            client[config.DB_NAME][config.COLL_NAME].insert_one({"job_id": config.jobs[0]["id"], "success": True, "message": "Test MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest Message", "timestamp": "2021-01-01T00:00:00.000Z", "command": "echo 'Hallo Welt'", "runtime": 3.0})
        for job in config.jobs:
            client[config.DB_NAME][config.COLL_NAME].insert_one({"job_id": job["id"], "success": False, "message": "Neuester Eintrag", "timestamp": "2021-01-01T00:00:00.000Z", "command": "notARealCommand 'Hallo Welt'", "runtime": 6.0})
        # Insert expired for last job
        client[config.DB_NAME][config.COLL_NAME].insert_one({"job_id": config.jobs[-1]["id"], "success": False, "expired": True, "message": "Test Message", "timestamp": "2021-01-01T00:00:00.000Z", "command": "echo 'Hallo Welt'", "runtime": 4.0})
        # Insert success for second last job
        client[config.DB_NAME][config.COLL_NAME].insert_one({"job_id": config.jobs[-2]["id"], "success": True, "message": "Test Message", "timestamp": "2021-01-01T00:00:00.000Z", "command": "echo 'Hallo Welt'", "runtime": 5.0})
        client.close()
        
    app.mongodb_client = MongoClient(config.MONGODB_CONNECTION_URI)
    app.database = app.mongodb_client[config.DB_NAME]
    # Test the connection
    app.database.command("serverStatus")
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
    
apiPrefix = "/api/v1"

from server.routes.jobs import jobsRouter

app.include_router(jobsRouter, prefix="/api/v1/jobs")

def run():
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'

    uvicorn.run("server.app:app", host="127.0.0.1" if config.DEV else "0.0.0.0", port=8000, reload=True)
    