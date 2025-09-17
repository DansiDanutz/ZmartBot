from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal

Kind = Literal["concept", "reasoning", "workspace"]

class MemoryIn(BaseModel):
    kind: Kind
    title: str = Field(..., min_length=1, max_length=256)
    body: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    timestamp: int
    ttl_days: Optional[int] = Field(default=None, ge=1, le=3650)

    @field_validator("tags")
    @classmethod
    def strip_tags(cls, v: List[str]) -> List[str]:
        return [t.strip() for t in v if t.strip()]

class SearchOut(BaseModel):
    id: str
    title: str
    snippet: str
    score: float
    tags: List[str] = []
