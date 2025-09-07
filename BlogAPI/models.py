import uuid

from database import Base
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    """
    User model representing a user table in the DB.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # A user can create multiple blogs
    blogs = relationship("Blog", back_populates="creator")


class Blog(Base):
    """
    Blog model representing a Blog table in DB.
    """
    __tablename__ = "blogs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String, index=True)
    body = Column(String, index=True)
    published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Foreign key → links to users.id
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    # Relationship → maps back to User
    creator = relationship("User", back_populates="blogs")
