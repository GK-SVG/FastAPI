from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class BlogBase(BaseModel):
    title: str
    body: str
    published: Optional[bool] = True

class BlogCreate(BlogBase):
    pass


class BlogResponse(BlogBase):
    id: UUID

    class Config:
        orm_mode = True