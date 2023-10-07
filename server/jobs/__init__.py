from server.config.config import DEV
from fastapi import HTTPException

class Jobs:
    def __init__(self) -> None:
        # Load the jobs (id, cron, grace period) from jobs.json
        self.jobs = []
        import json
        with open('jobs.json') as json_file:
            data = json.load(json_file)
            for key in data:
                self.jobs.append({"id": key, "cron": data[key]["cron"], "grace_time": data[key]["grace_time"], "waiting": False, "has_failed": False, "running": False})
        print(self.jobs) if DEV else None
        
    def update_job(self, id, had_failed=None, waiting=None, running=None):
        for j in self.jobs:
            if j["id"] == id:
                if had_failed is not None:
                    j["has_failed"] = had_failed
                if waiting is not None:
                    j["waiting"] = waiting
                if running is not None:
                    j["running"] = running
                break
            
    def verify_by_id(self, job_id):
        job = None
        for j in self.jobs:
            if j["id"] == job_id:
                job = j
                break
        if job is None:
            raise HTTPException(status_code=400, detail="Invalid Job ID")
        return job
    