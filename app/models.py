from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class ExtractRequest(BaseModel):
    url: HttpUrl


class ExtractResponse(BaseModel):
    title: str
    description: Optional[str] = None
    ingredients: List[str]
    instructions: List[str]
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    servings: Optional[int] = None
    tags: List[str] = []


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
