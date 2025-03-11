from typing import Optional

from pydantic import BaseModel

from utils.schemas.base import BaseSchema


class CategoryRequest(BaseModel):
    name: str
    description: Optional[str]


class CategoryResponse(BaseSchema, CategoryRequest):
    pass


class TopicRequest(BaseModel):
    name: str
    description: str
    category: str


class TopicResponse(BaseSchema):
    name: str
    description: str
    category_id: str
    high_score: Optional[float] = 0
    your_score: Optional[float] = 0
