from typing import Optional
import uuid;
from pydantic import BaseModel, Field
from typing import List
# from server.prisma.prisma import Prisma
from prisma.models import Job, JobRun
from datetime import datetime
# class Job(BaseModel):
#     id: str
#     cron: str
#     grace_time: int
#     waiting: bool
#     has_failed: bool
#     running: bool

# class JobResult(BaseModel):
#     id: str = Field(default_factory=uuid.uuid4, alias="_id")
#     job_id: str
#     success: bool
#     expired: Optional[bool] = False
#     message: Optional[str] = ""
#     command: Optional[str] = ""
#     runtime: Optional[float] = 0.0
#     timestamp: str
    
class JobResultResponse(BaseModel):
    job: Job
    # jobResults: List[JobRun]
    response: str
    
# class InsertJobResult(BaseModel):
#     job_id: str
#     success: bool
#     # expired: Optional[bool] = False
#     message: Optional[str] = ""
#     command: Optional[str] = ""
#     runtime: Optional[float] = 0.0
    
class InsertJobResultResponse(BaseModel):
    job: Job
    # jobResult: JobRun
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
    


# class JobResultList(BaseModel):
#     job_id: str
#     running: bool
#     results: List[JobRun]
