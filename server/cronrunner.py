import asyncio
from datetime import datetime
import aiocron
from server.config.config import APIKEY
from server.jobs import Jobs as JobsClass
jobs2 = JobsClass()
import requests
from server.prisma.prisma import prisma
from prisma.models import Job

APIURL = "http://localhost:8000/api/v1"

async def foo(job_id, grace_time):
    print(datetime.now().time(), "Running job", job_id)
    # Call the API /jobs/{id}/waiting 
    requests.put(APIURL + "/jobs/" + job_id + "/waiting", headers={"api-key": APIKEY})
    # Wait the grace period
    await asyncio.sleep(int(grace_time))
    # Trigger the job that should be executed
    requests.post(APIURL + "/jobs/" + job_id + "/grace_time_expired", headers={"api-key": APIKEY})
    


async def main():
    await prisma.connect()
    await jobs2.load_jobs_from_file_to_db()
    allJobs = await jobs2.get_all_jobs()
    print("ALL JOBS", allJobs)
    for job in allJobs:
        print(job.id, job.cron, job.grace_time)
        # await foo(job["id"],job["grace_time"])
        aiocron.crontab(job.cron, func=foo, args=(job.id,job.grace_time,), start=True)

    while True:
        await asyncio.sleep(1)

asyncio.run(main())