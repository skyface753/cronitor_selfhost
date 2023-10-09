from typing import Optional
from pydantic import BaseModel
from prisma.models import Job, JobRun
from datetime import datetime

class JobResultResponse(BaseModel):
    job: Job
    response: str

    
class InsertJobResultResponse(BaseModel):
    job: Job
    insertedRun: JobRun
    response: str
    
class InsertJobRun(BaseModel):
    job_id: str
    started_at: datetime
    finished_at: datetime
    is_success: bool
    error: Optional[str] = ""
    command: str
    output: Optional[str] = ""
    runtime: float
    

