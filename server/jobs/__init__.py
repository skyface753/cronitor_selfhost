from server.config.config import DEV
from fastapi import HTTPException
# from server.prisma.prisma import prisma
from prisma.models import Job, JobRun
from prisma.types import JobCreateInput, JobRunCreateInput
import json

class Jobs:
        
    async def load_jobs_from_file_to_db(self):
        # Load the jobs (id, cron, grace period) from jobs.json
        tmp = []
        with open('jobs.json') as json_file:
            data = json.load(json_file)
            for key in data:
                tmp.append({"id": key, "cron": data[key]["cron"], "grace_time": data[key]["grace_time"], "waiting": False, "has_failed": False, "running": False})
        # Set all jobs in database enabled to False
        await Job.prisma().update_many(where={}, data={"enabled": False})
        # Store the jobs in the database (if not already there)
        for job in tmp:
            jobInDB = await Job.prisma().find_first(where={"id": job["id"]})
            if not jobInDB:
                grace_time = int(job["grace_time"])
                newJob = JobCreateInput(id=job["id"], cron=job["cron"], grace_time=grace_time, is_waiting=False, is_running=False, has_failed=False, enabled=True)
                await Job.prisma().create(newJob)
            else:
                if jobInDB.cron != job["cron"] or jobInDB.grace_time != job["grace_time"]:
                    grace_time = int(job["grace_time"])
                    await Job.prisma().update(where={"id": job["id"]}, data={"cron": job["cron"], "grace_time": grace_time})
                await Job.prisma().update(where={"id": job["id"]}, data={"enabled": True})
                
    async def update_job(self, id, had_failed=None, waiting=None, running=None):
        # Update the job in the database
        update = {}
        if had_failed is not None:
            update["has_failed"] = had_failed
        if waiting is not None:
            update["is_waiting"] = waiting
        if running is not None:
            update["is_running"] = running
        await Job.prisma().update(where={"id": id}, data=update)
       
            
    async def verify_by_id(self, job_id):
        # Check if Job ID is valid
        job = await Job.prisma().find_first(where={"id": job_id}, include={"runsResults": False})
        if not job or job.enabled == False:
            raise HTTPException(status_code=400, detail="Invalid Job ID")
        return True

    async def get_all_jobs(self):
        # Get all jobs from the database
        allJobs = await Job.prisma().find_many(where={"enabled": True}, order={"id": "asc"})
        # 10 latest results for each job
        for job in allJobs:
            job.runsResults = await JobRun.prisma().find_many(where={"job_id": job.id}, order={"id": "desc"}, take=10)
        return allJobs
    

    async def create_dummy_data(self):
        # Delete all JobRuns
        await JobRun.prisma().delete_many()
        # Create dummy data
        allJobs = await Job.prisma().find_many(order={"id": "asc"})
        for job in allJobs:
            await JobRun.prisma().create(JobRunCreateInput(job_id=job.id, started_at="2021-01-01T00:00:00.000Z", finished_at="2021-01-01T00:00:00.000Z", is_success=False, error="failed", command="notARealCommand 'Hallo Welt'", output="ÄLTESTER", runtime=2.0))
        for i in range(10):
            await JobRun.prisma().create(JobRunCreateInput(job_id=allJobs[0].id, started_at="2021-01-01T00:00:00.000Z", finished_at="2021-01-01T00:00:00.000Z", is_success=True, error=None, command="echo 'Hallo Welt'", output="Test Message", runtime=3.0))
        for job in allJobs:
            await JobRun.prisma().create(JobRunCreateInput(job_id=job.id, started_at="2021-01-01T00:00:00.000Z", finished_at="2021-01-01T00:00:00.000Z", is_success=False, error="failed", command="notARealCommand 'Hallo Welt'", output="Neuester Eintrag", runtime=6.0))
        # Insert expired for last job
        await JobRun.prisma().create(JobRunCreateInput(job_id=allJobs[-1].id, started_at="2021-01-01T00:00:00.000Z", finished_at="2021-01-01T00:00:00.000Z", is_success=False, error="expired", command="notARealCommand 'Hallo Welt'", output="Test Message", runtime=4.0))
        # Insert success for second last job
        await JobRun.prisma().create(JobRunCreateInput(job_id=allJobs[-2].id, started_at="2021-01-01T00:00:00.000Z", finished_at="2021-01-01T00:00:00.000Z", is_success=True, error=None, command="echo 'Hallo Welt'", output="Test Message", runtime=5.0))
        print("Created dummy data") if DEV else None
        # Set all jobs to not waiting, not running and not failed
        for job in allJobs:
            await self.update_job(job.id, waiting=False, running=False, had_failed=False)