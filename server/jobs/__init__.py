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
                tmp.append({"id": key, "cron": data[key]["cron"], "grace_time": data[key]["grace_time"], "waiting": False, "has_failed": False, "running": False, "has_expired": False})
        # Set all jobs in database enabled to False
        await Job.prisma().update_many(where={}, data={"enabled": False})
        # Store the jobs in the database (if not already there)
        for job in tmp:
            jobInDB = await Job.prisma().find_first(where={"id": job["id"]})
            if not jobInDB:
                grace_time = int(job["grace_time"])
                newJob = JobCreateInput(id=job["id"], cron=job["cron"], grace_time=grace_time, is_waiting=False, is_running=False, has_failed=False, enabled=True, has_expired=False)
                await Job.prisma().create(newJob)
            else:
                if jobInDB.cron != job["cron"] or jobInDB.grace_time != job["grace_time"]:
                    grace_time = int(job["grace_time"])
                    await Job.prisma().update(where={"id": job["id"]}, data={"cron": job["cron"], "grace_time": grace_time})
                await Job.prisma().update(where={"id": job["id"]}, data={"enabled": True})
    
    
           
    async def update_job(self, id, had_failed=None, waiting=None, running=None, has_expired=None):
        # Update the job in the database
        update = {}
        if had_failed is not None:
            update["has_failed"] = had_failed
        if waiting is not None:
            update["is_waiting"] = waiting
        if running is not None:
            update["is_running"] = running
        if has_expired is not None:
            update["has_expired"] = has_expired
        await Job.prisma().update(where={"id": id}, data=update)
       
            
    async def verify_by_id(self, job_id, include_disabled=False):
        # Check if Job ID is valid
        job = await Job.prisma().find_first(where={"id": job_id}, include={"runsResults": False})
        if not job:
            raise HTTPException(status_code=400, detail="Invalid Job ID")
        if not job.enabled and not include_disabled:
            raise HTTPException(status_code=400, detail="Job is disabled")
        return True

    async def get_all_jobs(self, show_disabled=False):
        where_enabled = {"enabled": not show_disabled}
        # Get all jobs from the database
        allJobs = await Job.prisma().find_many( where=where_enabled, order={"id": "asc"})
        # 10 latest results for each job
        for job in allJobs:
            job.runsResults = await JobRun.prisma().find_many(where={"job_id": job.id}, order={"id": "desc"}, take=10)
        return allJobs
    
    async def create_dummy_data(self):
        await self.clear_db()
        await self.create_dummy_jobs()
        await self.create_dummy_runs()
        
    async def clear_db(self):
        await JobRun.prisma().delete_many()
        await Job.prisma().delete_many()
        
        
        
    async def create_dummy_jobs(self):
        should_success_job = JobCreateInput(id="should_success", cron="* * * * *", grace_time=10, is_waiting=False, is_running=False, has_failed=False, enabled=True)
        should_expired_job = JobCreateInput(id="should_expired", cron="* * * * *", grace_time=10, is_waiting=False, is_running=False, has_failed=False, enabled=True, has_expired=True)
        should_fail_job = JobCreateInput(id="should_fail", cron="* * * * *", grace_time=10, is_waiting=False, is_running=False, has_failed=True, enabled=True)
        should_be_disabled_job = JobCreateInput(id="should_be_disabled", cron="* * * * *", grace_time=10, is_waiting=False, is_running=False, has_failed=False, enabled=False)
        await Job.prisma().create(should_success_job)
        await Job.prisma().create(should_expired_job)
        await Job.prisma().create(should_fail_job)
        await Job.prisma().create(should_be_disabled_job)
    
    async def create_dummy_runs(self):
        # Create dummy data
        should_success_run1 = JobRunCreateInput(job_id="should_success", is_success=True, error="", output="Ältester Eintrag", command="echo 'Ältester Eintrag'", started_at="1999-01-01T00:00:00.000Z", finished_at="1999-01-01T00:00:00.000Z", runtime=2.0)
        should_success_run2 = JobRunCreateInput(job_id="should_success", is_success=True, error="", output="Neuester Eintrag", command="echo 'Neuester Eintrag'", started_at="2021-01-01T00:00:00.000Z", finished_at="2021-01-01T00:00:00.000Z", runtime=2.0)
        should_expired_run = JobRunCreateInput(job_id="should_expired", is_success=False, error="expired", output="", command="echo 'Hallo Welt'", started_at="2021-01-01T00:00:00.000Z", finished_at="2021-01-01T00:00:00.000Z", runtime=2.0)
        should_fail_run1 = JobRunCreateInput(job_id="should_fail", is_success=True, error="", output="", command="echo 'Hallo Welt'", started_at="2021-01-01T00:00:00.000Z", finished_at="2021-01-01T00:00:00.000Z", runtime=2.0)
        should_fail_run2 = JobRunCreateInput(job_id="should_fail", is_success=False, error="expired", output="", command="echo 'Hallo Welt'", started_at="2021-01-01T00:00:00.000Z", finished_at="2021-01-01T00:00:00.000Z", runtime=2.0)   
        should_fail_run = JobRunCreateInput(job_id="should_fail", is_success=False, error="failed", output="", command="echo 'Hallo Welt'", started_at="2021-01-01T00:00:00.000Z", finished_at="2021-01-01T00:00:00.000Z", runtime=2.0)
        should_be_disabled_run = JobRunCreateInput(job_id="should_be_disabled", is_success=False, error="failed", output="", command="echo 'Hallo Welt'", started_at="2021-01-01T00:00:00.000Z", finished_at="2021-01-01T00:00:00.000Z", runtime=2.0)
        await JobRun.prisma().create(should_success_run1)
        await JobRun.prisma().create(should_success_run2)
        await JobRun.prisma().create(should_expired_run)
        await JobRun.prisma().create(should_fail_run1)
        await JobRun.prisma().create(should_fail_run2)
        await JobRun.prisma().create(should_fail_run)
        await JobRun.prisma().create(should_be_disabled_run)
        