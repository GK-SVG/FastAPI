# SQLAlchemy models

from enum import Enum
import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class GenderChoice(str, Enum):
 male = "male"
 female = "female"


class RoleChoice(str, Enum):
 admin = "admin"
 user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    gender = Column(String, nullable=False)
    role = Column(String, nullable=False)
