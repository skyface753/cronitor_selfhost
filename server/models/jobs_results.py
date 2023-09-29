from typing import Optional
import uuid;
from pydantic import BaseModel, Field
from typing import List

class JobResult(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    job_id: str
    success: bool
    message: Optional[str]
    command: Optional[str]
    timestamp: str
    

    
class InsertJobResult(BaseModel):
    job_id: str
    success: bool
    message: Optional[str]
    command: Optional[str]
    
    
class JobResultList(BaseModel):
    job_id: str
    results: List[JobResult]