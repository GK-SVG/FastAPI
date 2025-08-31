# Pydantic schemas

from pydantic import BaseModel, EmailStr
from uuid import UUID
from models import GenderChoice, RoleChoice


class UserBase(BaseModel):
    name: str
    email: EmailStr
    gender: GenderChoice
    role: RoleChoice


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: UUID

    class Config:
        orm_mode = True