from pydantic import BaseModel
from typing import List, Optional

class ResolveRequest(BaseModel):
    disbursement_ids: List[str]

class ResolveResponse(BaseModel):
    id: str
    fa: str
    name: Optional[str] = None
