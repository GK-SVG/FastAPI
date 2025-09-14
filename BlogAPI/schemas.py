from pydantic import BaseModel
from typing import Optional
from uuid import UUID

# User Schemas
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Blog Schemas
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