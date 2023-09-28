from fastapi import FastAPI, Query, HTTPException, Path, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

APIKEY = os.environ.get("APIKEY")
if APIKEY is None:
    raise Exception("APIKEY not set")

# Load the jobs (id, cron, grace period) from jobs.json
jobs = []
import json
with open('jobs.json') as json_file:
    data = json.load(json_file)
    for key in data:
        jobs.append({"id": key, "cron": data[key]["cron"], "grace_time": data[key]["grace_time"]})

print(jobs)

DEV = os.environ.get("DEV") or False
if DEV:
    print("Running in DEV mode")
    
app = FastAPI()

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGODB_CONNECTION_URI = "mongodb://admin:admin@127.0.0.1:27017/jobs_db_dev?authSource=admin"
MONGODB_CONNECTION_URI = os.environ.get("MONGODB_CONNECTION_URI") or MONGODB_CONNECTION_URI

DB_NAME="jobs_db_dev"
DB_NAME = os.environ.get("DB_NAME") or DB_NAME

COLL_NAME = "job_results"
COLL_NAME = os.environ.get("COLL_NAME") or COLL_NAME

from pymongo import MongoClient
@app.on_event("startup")
def startup_db_client():
    if DEV:
        # Clear the database
        client = MongoClient(MONGODB_CONNECTION_URI)

        client.drop_database(DB_NAME)
        # Insert some test data
        for job in jobs:
            client[DB_NAME][COLL_NAME].insert_one({"job_id": job["id"], "success": False, "message": "ÄLTESTER", "timestamp": "2021-01-01T00:00:00.000Z"})
        for i in range(10):
            client[DB_NAME][COLL_NAME].insert_one({"job_id": jobs[0]["id"], "success": True, "message": "Test Message", "timestamp": "2021-01-01T00:00:00.000Z"})
        for job in jobs:
            client[DB_NAME][COLL_NAME].insert_one({"job_id": job["id"], "success": False, "message": "Neuester Eintrag", "timestamp": "2021-01-01T00:00:00.000Z"})
        client.close()
        
    app.mongodb_client = MongoClient(MONGODB_CONNECTION_URI)
    app.database = app.mongodb_client[DB_NAME]
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
    
apiPrefix = "/api/v1"


from fastapi import APIRouter, Body, Request, Response, HTTPException, status




from server.models.jobs_results import JobResult, InsertJobResult
from fastapi import Body, Request, status, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import List
from pydantic import BaseModel

jobsRouter = APIRouter()


class JobResultList(BaseModel):
    job_id: str
    results: List[JobResult]
 
def check_api_key(api_key: str):
    if api_key != APIKEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
def check_job_id(job_id: str):
    job = None
    for j in jobs:
        if j["id"] == job_id:
            job = j
            break
    if job is None:
        raise HTTPException(status_code=400, detail="Invalid Job ID")
    return job


   
def get_results_for_a_job(job_id: str, request: Request, limit: int =   0):
    jobResult = request.app.database[COLL_NAME].find({"job_id": job_id}, sort=[('_id', -1)], limit=limit)
    # print(jobResult)
    jobResultList = []
    for result in jobResult:
        result["_id"] = str(result["_id"])
        jobResultList.append(result)
    return jobResultList

@jobsRouter.get("/", response_description="list all jobs and their result", response_model=List[JobResultList])
def list_all_jobs(request: Request):
    # Get for each job the 10 latest results
    jobResults = []
    for job in jobs:
        jobResults.append({"job_id": job["id"], "results": get_results_for_a_job(job["id"], request, 10)})
    print(jobResults)
    return jobResults



@jobsRouter.get("/{job_id}", response_description="get a job result", response_model=List[JobResult])
def list_job(job_id: str, request: Request):
    job = check_job_id(job_id)
    return get_results_for_a_job(job_id, request)
2
@jobsRouter.post("/{job_id}", response_description='insert a job result', status_code=status.HTTP_201_CREATED,response_model=JobResult)
def insert_job_result(request: Request, jobResult: InsertJobResult = Body(...), api_key: str = Body(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    job = check_job_id(jobResult.job_id)
    # Insert Job Result
    jobResult = jsonable_encoder(jobResult)
    new_jobResult_item = request.app.database[COLL_NAME].insert_one(jobResult)
    # print("new", new_jobResult_item)
    created_jobResult_item = request.app.database[COLL_NAME].find_one({
        "_id": new_jobResult_item.inserted_id
    })
    created_jobResult_item["_id"] = str(created_jobResult_item["_id"])
    return created_jobResult_item



    
app.include_router(jobsRouter, prefix="/api/v1/jobs")

def run():
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=True)
# if __name__ == "__main__":
#     uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=True)