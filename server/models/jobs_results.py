from typing import Optional
import uuid;
from pydantic import BaseModel, Field
from typing import List

class Job(BaseModel):
    id: str
    cron: str
    grace_time: int
    waiting: bool
    has_failed: bool

class JobResult(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    job_id: str
    success: bool
    expired: Optional[bool] = False
    message: Optional[str] = ""
    command: Optional[str] = ""
    runtime: Optional[float] = 0.0
    timestamp: str
    

    
class InsertJobResult(BaseModel):
    job_id: str
    success: bool
    # expired: Optional[bool] = False
    message: Optional[str] = ""
    command: Optional[str] = ""
    runtime: Optional[float] = 0.0
    
class InsertJobResultResponse(BaseModel):
    job: Job
    jobResult: JobResult
    response: str
    
    
class JobResultList(BaseModel):
    job_id: str
    results: List[JobResult]
