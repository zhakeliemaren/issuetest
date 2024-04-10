from typing import Optional
from fastapi.datastructures import Default
from pydantic import BaseModel
from datetime import datetime


class Log(BaseModel):
    id: int
    sync_job_id: int
    commit_id: Optional[int]
    pull_request_id: Optional[int]
    log_type: str
    log: str
    create_time: datetime
