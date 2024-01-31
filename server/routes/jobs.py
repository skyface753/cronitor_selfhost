import server.config.config as config
from fastapi import APIRouter, HTTPException, status, Header
from typing import List
from server.models.jobs_results import InsertJobRun, InsertJobResultResponse, JobResultResponse
from fastapi import APIRouter,  status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
import server.notifications.notify as notify
from server.jobs import Jobs as JobsClass
from prisma.models import JobRun, Job
from prisma.types import JobRunCreateInput
from prisma.enums import JobRunResult
import datetime
jobs = JobsClass()

jobsRouter = APIRouter()


def check_api_key(api_key: str):
    if api_key != config.APIKEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
 


@jobsRouter.get("/", response_description="list all jobs and their result", response_model=List[Job])
async def list_all_jobs(show_disabled: bool = False):
    # Get for each job the 10 latest results
    jobResults = await jobs.get_all_jobs(show_disabled)
    # print(jobResults)
    return jobResults

@jobsRouter.delete("/{job_id}", response_description="delete a disabled job", status_code=status.HTTP_200_OK)
async def delete_disabled_job(job_id: str, api_key: str = Header(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    await jobs.verify_by_id(job_id, include_disabled=True)
    # Check if Job is disabled
    job = await Job.prisma().find_first(where={"id": job_id, "enabled": False})
    if not job:
        raise HTTPException(status_code=400, detail="Job is not disabled! Please remove the job from the jobs.json file and restart the server!")
    # Delete the runs
    await JobRun.prisma().delete_many(where={"job_id": job_id})
    # Delete the job
    await Job.prisma().delete(where={"id": job_id})
    return {"message": "Job deleted"}

@jobsRouter.get("/{job_id}", response_description="get a job result", response_model=JobResultResponse)
async def list_job(job_id: str, all_results: bool = False):
    await jobs.verify_by_id(job_id)
    job = await Job.prisma().find_first(where={"id": job_id, "enabled": True}, include={"runsResults": False})
    # Get all runs for the job
    if all_results:
        runs = await JobRun.prisma().find_many(where={"job_id": job_id}, include={"job": False})
    else:
        # Get the latest 30 runs for the job
        runs = await JobRun.prisma().find_many(where={"job_id": job_id}, take=30, include={"job": False}, order={"finished_at": "desc"})
    job.runsResults = runs
    return JobResultResponse(job=job, response="OK")
    





@jobsRouter.post("/insert", response_description='insert a job result', status_code=status.HTTP_201_CREATED,response_model=InsertJobResultResponse)
async def insert_job_result( api_key: str = Header(...),jobResult: InsertJobRun = Depends(InsertJobRun.as_form)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    # job = check_job_id(jobResult.job_id)
    await jobs.verify_by_id(jobResult.job_id)
    
    # Insert Job Result
    jobResult = jsonable_encoder(jobResult)
    # Set the timestamp to the current time
    jobResult["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    newJobRun = JobRunCreateInput(job_id=jobResult["job_id"], started_at=jobResult["started_at"], finished_at=jobResult["finished_at"], result=jobResult["result"], command=jobResult["command"], output=jobResult["output"], runtime=jobResult["runtime"])
    newJobRun = await JobRun.prisma().create(newJobRun)
    await jobs.verify_by_id(jobResult["job_id"])
    job = await Job.prisma().find_first(where={"id": jobResult["job_id"], "enabled": True}, include={"runsResults": False})
    response = "OK"
    # if jobResult["is_success"] == False: # Job failed
    if jobResult["result"] == JobRunResult.FAILED: # Job failed
        notify.send_notification(jobResult["job_id"], "failed", jobResult["output"], jobResult["command"])
        await jobs.update_job(jobResult["job_id"], True, False, False, has_expired=False)
        response = "Job failed -> Notify"
    else:
        if job.has_failed == True:
            notify.send_notification(jobResult["job_id"], "resolved")
            response = "Job resolved -> Notify"
        elif job.is_waiting == False:
            notify.send_notification(jobResult["job_id"], "was_not_waiting")
            response = "Job was not waiting -> Notify"
        await jobs.update_job(jobResult["job_id"], False, False, False, has_expired=False)
    job = await Job.prisma().find_first(where={"id": jobResult["job_id"]}, include={"runsResults": False})
    insertJobResultResponse = InsertJobResultResponse(job=job, response=response, insertedRun=newJobRun)
    return insertJobResultResponse

@jobsRouter.post("/start", response_description='set running state of a job', status_code=status.HTTP_200_OK)
async def set_running_state(job_id: str, api_key: str = Header(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    # job = check_job_id(job_id)
    await jobs.verify_by_id(job_id)
    
    # Set the running state of the job
    # update_job(job_id, None, None, True)
    await jobs.update_job(job_id, None, None, True, has_expired=False)
    return {"message": "Job running state set to: True"}

@jobsRouter.put("/{job_id}/waiting", response_description='set waiting state of a job', status_code=status.HTTP_200_OK)
async def set_waiting_state(job_id: str, api_key: str = Header(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    # job = check_job_id(job_id)
    await jobs.verify_by_id(job_id)
    # Set the waiting state of the job
    # update_job(job_id, None, True, None)
    await jobs.update_job(job_id, None, True, None, has_expired=False)
    return {"message": "Job waiting state set to: True"}
    
@jobsRouter.post("/{job_id}/grace_time_expired", response_description='grace time expired', status_code=status.HTTP_200_OK)
async def grace_time_expired(job_id: str, api_key: str = Header(...)):
    # Check if API Key is valid
    check_api_key(api_key)
    # Check if Job ID is valid
    await jobs.verify_by_id(job_id)
    job = await Job.prisma().find_first(where={"id": job_id}, include={"runsResults": False})
    # Check if the job is waiting
    if job.is_waiting == False:
        return {"message": "Job was not waiting"}
    if config.DEV:
        print("Grace time expired")
    # Set the job to failed
    notify.send_notification(job_id, "expired")
    newJobRun = JobRunCreateInput(job_id=job_id,result=JobRunResult.EXPIRED, command="", runtime=0.0, started_at=datetime.datetime.utcnow(), finished_at=datetime.datetime.utcnow())
    await JobRun.prisma().create(newJobRun)
    await jobs.update_job(job_id, False, False, False, has_expired=True)
    return {"message": "Grace time expired -> Notify"}
