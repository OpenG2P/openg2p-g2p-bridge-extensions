from typing import List, Optional

from pydantic import BaseModel


class ResolveRequest(BaseModel):
    beneficiary_ids: List[str]


class ResolveResult(BaseModel):
    id: str
    fa: dict
    name: Optional[str] = None


class ResolveResponse(BaseModel):
    results: List[ResolveResult]
