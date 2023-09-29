import server.config.config as config
from fastapi import APIRouter, Body, HTTPException, Request, status
from typing import List
from server.models.jobs_results import JobResult, InsertJobResult, JobResultList
from fastapi import APIRouter, Body, Request, status, HTTPException
from fastapi.encoders import jsonable_encoder
import server.mail.mail as mail
jobsRouter = APIRouter()


def check_api_key(api_key: str):
    if api_key != config.APIKEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
def check_job_id(job_id: str):
    job = None
    for j in config.jobs:
        if j["id"] == job_id:
            job = j
            break
    if job is None:
        raise HTTPException(status_code=400, detail="Invalid Job ID")
    return job


   
def get_results_for_a_job(job_id: str, request: Request, limit: int =   0):
    jobResult = request.app.database[config.COLL_NAME].find({"job_id": job_id}, sort=[('_id', -1)], limit=limit)
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
    for job in config.jobs:
        jobResults.append({"job_id": job["id"], "results": get_results_for_a_job(job["id"], request, 10)})
    # print(jobResults)
    return jobResults



@jobsRouter.get("/{job_id}", response_description="get a job result", response_model=List[JobResult])
def list_job(job_id: str, request: Request):
    job = check_job_id(job_id)
    return get_results_for_a_job(job_id, request)

import datetime

@jobsRouter.post("/{job_id}", response_description='insert a job result', status_code=status.HTTP_201_CREATED,response_model=JobResult)
def insert_job_result(request: Request, jobResult: InsertJobResult = Body(...), api_key: str = Body(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    job = check_job_id(jobResult.job_id)
    # Insert Job Result
    jobResult = jsonable_encoder(jobResult)
    # Set the timestamp to the current time
    jobResult["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    new_jobResult_item = request.app.database[config.COLL_NAME].insert_one(jobResult)
    # print("new", new_jobResult_item)
    created_jobResult_item = request.app.database[config.COLL_NAME].find_one({
        "_id": new_jobResult_item.inserted_id
    })
    created_jobResult_item["_id"] = str(created_jobResult_item["_id"])
    if jobResult["success"] == False:
        mail.send_email(jobResult["job_id"], jobResult["success"], jobResult["message"], jobResult["command"])
    return created_jobResult_item

