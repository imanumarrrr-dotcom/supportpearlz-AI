from typing import Literal
from pydantic import BaseModel, Field

class SupportAnswer(BaseModel):
    answer: str = Field(description="Customer-facing grounded answer")
    sources: list[str] = Field(default_factory=list, description="Only supplied source labels actually used")
    confidence: Literal["high", "partial", "none"] = "none"
    answered: bool = False
