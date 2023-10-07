import server.config.config as config
from fastapi import APIRouter, Body, HTTPException, Request, status, Header
from typing import List
from server.models.jobs_results import JobResult, InsertJobResult, JobResultList, InsertJobResultResponse, JobResultResponse
from fastapi import APIRouter, Body, Request, status, HTTPException
from fastapi.encoders import jsonable_encoder
import server.notifications.notify as notify
from server.jobs import Jobs as JobsClass
jobs = JobsClass()

jobsRouter = APIRouter()


def check_api_key(api_key: str):
    if api_key != config.APIKEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
 


   
def get_results_for_a_job(job_id: str, request: Request, limit: int = 0, exclude_messages: bool = False):
    jobResult = request.app.database[config.COLL_NAME].find({"job_id": job_id}, sort=[('_id', -1)], limit=limit)
    jobResultList = []
    for result in jobResult:
        result["_id"] = str(result["_id"])
        if exclude_messages:
            result["message"] = ""
        jobResultList.append(result)
    return jobResultList


@jobsRouter.get("/", response_description="list all jobs and their result", response_model=List[JobResultList])
def list_all_jobs(request: Request):
    # Get for each job the 10 latest results
    jobResults = []
    for job in jobs.jobs:
        jobResults.append({"job_id": job["id"], "running": job["running"], "results": get_results_for_a_job(job["id"], request, 10, True)})
    # print(jobResults)
    return jobResults



@jobsRouter.get("/{job_id}", response_description="get a job result", response_model=JobResultResponse)
def list_job(job_id: str, request: Request):
    # job = check_job_id(job_id)
    job = jobs.verify_by_id(job_id)
    return JobResultResponse(job=job, jobResults=get_results_for_a_job(job_id, request), response="OK")
    

import datetime



@jobsRouter.post("/insert", response_description='insert a job result', status_code=status.HTTP_201_CREATED,response_model=InsertJobResultResponse)
def insert_job_result(request: Request, jobResult: InsertJobResult = Body(...), api_key: str = Header(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    # job = check_job_id(jobResult.job_id)
    job = jobs.verify_by_id(jobResult.job_id)
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
    response = "OK"
    if jobResult["success"] == False: # Job failed
        # notify.send_failed(jobResult["job_id"], jobResult["message"], jobResult["command"])
        notify.send_notification(jobResult["job_id"], "failed", jobResult["message"], jobResult["command"])
        # update_job(jobResult["job_id"], True, False, False)
        jobs.update_job(jobResult["job_id"], True, False, False)
        response = "Job failed -> Notify"
    else:
        # Set job waiting to false
        for j in jobs.jobs:
            if j["id"] == jobResult["job_id"]:
                if j["has_failed"] == True:
                    # notify.send_resolved(jobResult["job_id"])
                    notify.send_notification(jobResult["job_id"], "resolved")
                    response = "Job resolved -> Notify"
                elif j["waiting"] == False:
                    # notify.send_was_not_waiting(jobResult["job_id"])
                    notify.send_notification(jobResult["job_id"], "was_not_waiting")
                    response = "Job was not waiting -> Notify"
                # update_job(jobResult["job_id"], False, False, False)
                jobs.update_job(jobResult["job_id"], False, False, False)
                break
    insertJobResultResponse = InsertJobResultResponse(job=job, jobResult=created_jobResult_item, response=response)
    return insertJobResultResponse

@jobsRouter.post("/start", response_description='set running state of a job', status_code=status.HTTP_200_OK)
def set_running_state(request: Request, job_id: str, api_key: str = Header(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    # job = check_job_id(job_id)
    job = jobs.verify_by_id(job_id)
    # Set the running state of the job
    # update_job(job_id, None, None, True)
    jobs.update_job(job_id, None, None, True)
    return {"message": "Job running state set to true"}

@jobsRouter.put("/{job_id}/waiting", response_description='set waiting state of a job', status_code=status.HTTP_200_OK)
def set_waiting_state(request: Request, job_id: str, api_key: str = Header(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    # job = check_job_id(job_id)
    job = jobs.verify_by_id(job_id)
    # Set the waiting state of the job
    # update_job(job_id, None, True, None)
    jobs.update_job(job_id, None, True, None)
    return {"message": "Job waiting state set to true"}
    
@jobsRouter.post("/{job_id}/grace_time_expired", response_description='grace time expired', status_code=status.HTTP_200_OK)
def grace_time_expired(request: Request, job_id: str, api_key: str = Header(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    # job = check_job_id(job_id)
    job = jobs.verify_by_id(job_id)
    # Check if the job is waiting
    wasWaiting = False
    for j in jobs.jobs:
        if j["id"] == job_id:
            wasWaiting = j["waiting"]
            break
    if wasWaiting:
        if config.DEV:
            print("Jobs was waiting and did not execute in time!")
        # notify.send_expired(job_id)
        notify.send_notification(job_id, "expired")
        newJobResult = {"job_id": job_id, "success": False, "expired": True}
        newJobResult["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
        new_jobResult_item = request.app.database[config.COLL_NAME].insert_one(newJobResult)
        created_jobResult_item = request.app.database[config.COLL_NAME].find_one({
            "_id": new_jobResult_item.inserted_id
        })
        created_jobResult_item["_id"] = str(created_jobResult_item["_id"])
        return {"message": "Job was waiting and did not execute in time!"}
    else:
        if config.DEV:
            print("Perfekt ausgeführt")
        return {"message": "Job was not waiting"}
