from pydantic import BaseModel
from typing import Optional

class Query(BaseModel):
    file_id: str  # Always required to identify the uploaded file
    age: Optional[int] = None
    gender: Optional[str] = None
    procedure: Optional[str] = None
    location: Optional[str] = None
    policy_duration_months: Optional[int] = None
