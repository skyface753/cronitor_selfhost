from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from server.prisma.prisma import prisma
# from pymongo import MongoClient
from server.jobs import Jobs as JobsClass
newJobs = JobsClass()



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



@app.on_event("startup")
async def startup_db_client():
    
    # if config.DEV:
        # Clear the database
        # client = MongoClient(config.MONGODB_CONNECTION_URI)
        # print(config.MONGODB_CONNECTION_URI)
        # client.drop_database(config.DB_NAME)
        # TODO: JOBS!
        # Insert some test data
        # for job in newJobs.internalJobs:
        #     client[config.DB_NAME][config.COLL_NAME].insert_one({"job_id": job["id"], "success": False, "message": "ÄLTESTER", "timestamp": "2021-01-01T00:00:00.000Z", "command": "notARealCommand 'Hallo Welt'", "runtime": 2.0})
        # for i in range(10):
        #     client[config.DB_NAME][config.COLL_NAME].insert_one({"job_id": newJobs.internalJobs[0]["id"], "success": True, "message": "Test MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest MessageTest Message", "timestamp": "2021-01-01T00:00:00.000Z", "command": "echo 'Hallo Welt'", "runtime": 3.0})
        # for job in newJobs.internalJobs:
        #     client[config.DB_NAME][config.COLL_NAME].insert_one({"job_id": job["id"], "success": False, "message": "Neuester Eintrag", "timestamp": "2021-01-01T00:00:00.000Z", "command": "notARealCommand 'Hallo Welt'", "runtime": 6.0})
        # Insert expired for last job
        # client[config.DB_NAME][config.COLL_NAME].insert_one({"job_id": newJobs.internalJobs[-1]["id"], "success": False, "expired": True, "message": "Test Message", "timestamp": "2021-01-01T00:00:00.000Z", "command": "echo 'Hallo Welt'", "runtime": 4.0})
        # Insert success for second last job
        # client[config.DB_NAME][config.COLL_NAME].insert_one({"job_id": newJobs.internalJobs[-2]["id"], "success": True, "message": "Test Message", "timestamp": "2021-01-01T00:00:00.000Z", "command": "echo 'Hallo Welt'", "runtime": 5.0})
        # client.close()
    # app.mongodb_client = MongoClient(config.MONGODB_CONNECTION_URI)
    # app.database = app.mongodb_client[config.DB_NAME]
    # # Test the connection
    # app.database.command("serverStatus")
    # print("Connected to the MongoDB database!")
    await prisma.connect()
    print("Connected to the Prisma database!")
    await newJobs.load_jobs_from_file_to_db()
    if config.DEV:
        print("Loaded jobs from file to DB")
        print("Creating dummy data")
        await newJobs.create_dummy_data()
        

@app.on_event("shutdown")
async def shutdown_db_client():
    # app.mongodb_client.close()
    await prisma.disconnect()
    
apiPrefix = "/api/v1"

from server.routes.jobs import jobsRouter
import random
import string
app.include_router(jobsRouter, prefix="/api/v1/jobs")

@app.get("/testPrisma")
async def root():
    # Insert a new user
    #Random mail
    mail = ''.join(random.choice(string.ascii_letters) for i in range(10))
    newUser = await prisma.user.create(
        data={
            'name': 'Robert',
            'email': mail + '@example.com',
        },
    )
    # Get all users
    result = await prisma.user.find_many()
    return result

def run():
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'

    uvicorn.run("server.app:app", host="127.0.0.1" if config.DEV else "0.0.0.0", port=8000, reload=True)
    