from typing import List, Optional

from pydantic import BaseModel


class ResolveRequest(BaseModel):
    beneficiary_ids: List[str]


class ResolveResult(BaseModel):
    id: Optional[str] = None
    fa: Optional[dict] = None
    name: Optional[str] = None
    status: Optional[str] = None
    status_reason_code: Optional[str] = None


class ResolveResponse(BaseModel):
    results: List[ResolveResult]
