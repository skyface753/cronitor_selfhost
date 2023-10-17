from typing import Optional
from pydantic import BaseModel
from prisma.models import Job, JobRun
from datetime import datetime
from fastapi import Form
from prisma.enums import JobRunResult

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
    result: JobRunResult
    command: str
    output: Optional[str] = ""
    runtime: float
    
    @classmethod
    def as_form(cls, job_id: str = Form(...), started_at: datetime = Form(...), finished_at: datetime = Form(...), is_success: bool = Form(...), command: str = Form(...), output: Optional[str] = Form(""), runtime: float = Form(...)):
        return cls(job_id=job_id, started_at=started_at, finished_at=finished_at, result=JobRunResult.SUCCESS if is_success else JobRunResult.FAILED, command=command, output=output, runtime=runtime)
    

