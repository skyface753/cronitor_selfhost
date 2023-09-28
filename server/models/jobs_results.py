from typing import Optional
import uuid;
from pydantic import BaseModel, Field


class JobResult(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    job_id: str
    success: bool
    message: Optional[str]
    timestamp: str
    

    
class InsertJobResult(BaseModel):
    job_id: str
    success: bool
    message: Optional[str]
    timestamp: str
    