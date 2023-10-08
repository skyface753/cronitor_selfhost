import server.config.config as config
from fastapi import APIRouter, Body, HTTPException, Request, status, Header
from typing import List
from server.models.jobs_results import InsertJobRun, InsertJobResultResponse, JobResultResponse
from fastapi import APIRouter, Body, Request, status, HTTPException
from fastapi.encoders import jsonable_encoder
import server.notifications.notify as notify
from server.prisma.prisma import prisma
from server.jobs import Jobs as JobsClass
from prisma.models import JobRun, Job
from prisma.types import JobRunCreateInput
jobs = JobsClass()

jobsRouter = APIRouter()


def check_api_key(api_key: str):
    if api_key != config.APIKEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
 


@jobsRouter.get("/", response_description="list all jobs and their result", response_model=List[Job])
async def list_all_jobs():
    # Get for each job the 10 latest results
    jobResults = await jobs.get_all_jobs()
    # print(jobResults)
    return jobResults



@jobsRouter.get("/{job_id}", response_description="get a job result", response_model=JobResultResponse)
async def list_job(job_id: str):
    # job = check_job_id(job_id)
    job = await jobs.verify_by_id(job_id)
    return JobResultResponse(job=job, response="OK")
    

import datetime



@jobsRouter.post("/insert", response_description='insert a job result', status_code=status.HTTP_201_CREATED,response_model=InsertJobResultResponse)
async def insert_job_result(jobResult: InsertJobRun = Body(...), api_key: str = Header(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    # job = check_job_id(jobResult.job_id)
    job = await jobs.verify_by_id(jobResult.job_id)
    print("Job", job)
    # Insert Job Result
    jobResult = jsonable_encoder(jobResult)
    # Set the timestamp to the current time
    jobResult["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    errorType = "" if jobResult["is_success"] else "failed"
    newJobRun = JobRunCreateInput(job_id=jobResult["job_id"], started_at=jobResult["started_at"], finished_at=jobResult["finished_at"], is_success=jobResult["is_success"], error=errorType, command=jobResult["command"], output=jobResult["output"], runtime=jobResult["runtime"])
    await JobRun.prisma().create(newJobRun)
    job = await jobs.verify_by_id(jobResult["job_id"])
    response = "OK"
    if jobResult["is_success"] == False: # Job failed
        notify.send_notification(jobResult["job_id"], "failed", jobResult["output"], jobResult["command"])
        await jobs.update_job(jobResult["job_id"], True, False, False)
        response = "Job failed -> Notify"
    else:
        if job.has_failed == True:
            notify.send_notification(jobResult["job_id"], "resolved")
            response = "Job resolved -> Notify"
        elif job.is_waiting == False:
            notify.send_notification(jobResult["job_id"], "was_not_waiting")
            response = "Job was not waiting -> Notify"
        await jobs.update_job(jobResult["job_id"], False, False, False)
    insertJobResultResponse = InsertJobResultResponse(job=job, jobResult=newJobRun, response=response)
    return insertJobResultResponse

@jobsRouter.post("/start", response_description='set running state of a job', status_code=status.HTTP_200_OK)
async def set_running_state(job_id: str, api_key: str = Header(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    # job = check_job_id(job_id)
    job = await jobs.verify_by_id(job_id)
    # Set the running state of the job
    # update_job(job_id, None, None, True)
    await jobs.update_job(job_id, None, None, True)
    return {"message": "Job running state set to true"}

@jobsRouter.put("/{job_id}/waiting", response_description='set waiting state of a job', status_code=status.HTTP_200_OK)
async def set_waiting_state(job_id: str, api_key: str = Header(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    # job = check_job_id(job_id)
    job = await jobs.verify_by_id(job_id)
    # Set the waiting state of the job
    # update_job(job_id, None, True, None)
    await jobs.update_job(job_id, None, True, None)
    return {"message": "Job waiting state set to true"}
    
@jobsRouter.post("/{job_id}/grace_time_expired", response_description='grace time expired', status_code=status.HTTP_200_OK)
async def grace_time_expired(job_id: str, api_key: str = Header(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    # job = check_job_id(job_id)
    job = await jobs.verify_by_id(job_id)
    # Check if the job is waiting
    if job.is_waiting == False:
        raise HTTPException(status_code=400, detail="Job was not waiting")
    if config.DEV:
        print("Grace time expired")
    # Set the job to failed
    notify.send_notification(job_id, "expired")
    newJobRun = JobRunCreateInput(job_id=job_id, is_success=False, error="expired", command="", runtime=0.0, started_at=datetime.datetime.utcnow(), finished_at=datetime.datetime.utcnow())
    await JobRun.prisma().create(newJobRun)
    # await jobs.update_job(job_id, True, False, False)
    return {"message": "Grace time expired"}
    # if wasWaiting:
    #     if config.DEV:
    #         print("Jobs was waiting and did not execute in time!")
    #     # notify.send_expired(job_id)
    #     notify.send_notification(job_id, "expired")
    #     newJobResult = {"job_id": job_id, "success": False, "expired": True}
    #     newJobResult["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    #     newJobRun = JobRun(**newJobResult)
    #     await JobRun.prisma().create(newJobRun)
    #     # new_jobResult_item = request.app.database[config.COLL_NAME].insert_one(newJobResult)
    #     # created_jobResult_item = request.app.database[config.COLL_NAME].find_one({
    #     #     "_id": new_jobResult_item.inserted_id
    #     # })
    #     # created_jobResult_item["_id"] = str(created_jobResult_item["_id"])
    #     return {"message": "Job was waiting and did not execute in time!"}
    # else:
    #     if config.DEV:
    #         print("Perfekt ausgeführt")
    #     return {"message": "Job was not waiting"}
