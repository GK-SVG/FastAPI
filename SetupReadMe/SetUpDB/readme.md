# FastAPI — Database Models & Pydantic Schemas

This README explains, step-by-step, how to set up **database models** (SQLAlchemy) and **Pydantic schemas** in a FastAPI project. Includes examples for relationships, CRUD helpers, and how to wire everything into FastAPI endpoints.

---

## 📦 Requirements
- Python 3.9+
- FastAPI
- Uvicorn (ASGI server)
- SQLAlchemy (sync example in this README)
- (Optional) Alembic for migrations
- (Optional) psycopg2-binary for PostgreSQL

Install the essentials:
```bash
pip install fastapi uvicorn sqlalchemy pydantic
# If using PostgreSQL:
pip install psycopg2-binary
# For migrations:
pip install alembic
```

---

## 🗂 Project structure (recommended)
```
project/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── __init__.py
├── alembic/                # (if using alembic)
├── alembic.ini             # (if using alembic)
└── README.md
```

---

## 1) `database.py` — create engine, session and Base (sync SQLAlchemy)
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# read from env or default to sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

---

## 2) `models.py` — SQLAlchemy models (User <-> Blog example)
```python
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)

    # Python-side relationship (not a DB column)
    # back_populates points to Blog.creator
    blogs = relationship("Blog", back_populates="creator", cascade="all, delete-orphan")


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)

    # The actual DB column that links to users.id
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Python-side relationship (not a DB column)
    # back_populates points to User.blogs
    creator = relationship("User", back_populates="blogs")
```

Notes:
- `ForeignKey("users.id")` creates the DB-level connection.
- `relationship(...)` creates Python/ORM-level convenience attributes (`user.blogs`, `blog.creator`).
- `back_populates` wires the two `relationship()` attributes so updates stay in sync.

---

## 3) `schemas.py` — Pydantic models for request/response validation
```python
from pydantic import BaseModel
from typing import List, Optional

class BlogBase(BaseModel):
    title: str
    content: str

class BlogCreate(BlogBase):
    pass

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

# Response schemas with id fields
class BlogResponse(BlogBase):
    id: int
    created_by: int

    class Config:
        orm_mode = True

class UserResponse(UserBase):
    id: int
    blogs: List[BlogResponse] = []

    class Config:
        orm_mode = True
```

Important:
- `orm_mode = True` allows Pydantic to read SQLAlchemy ORM objects (not just plain dicts).
- Nested schemas let FastAPI return user + user's blogs together.

---

## 4) `crud.py` — helper functions to interact with DB (sync)
```python
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from . import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_with_blogs(db: Session, user_id: int):
    # joinedload avoids extra lazy queries
    return db.query(models.User).options(joinedload(models.User.blogs)).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_blog(db: Session, blog: schemas.BlogCreate, user_id: int):
    db_blog = models.Blog(title=blog.title, content=blog.content, created_by=user_id)
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog
```

---

## 5) `main.py` — FastAPI app wiring endpoints
```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine, Base

# create tables (for quick dev; use Alembic for prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI SQLAlchemy Example")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_with_blogs(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/blogs/", response_model=schemas.BlogResponse)
def create_blog(blog: schemas.BlogCreate, user_id: int, db: Session = Depends(get_db)):
    # ensure user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_blog(db=db, blog=blog, user_id=user_id)
```

---

## 6) Migrations (Alembic) — short notes
1. Initialize alembic (project root):
```bash
alembic init alembic
```

2. In `alembic/env.py`, import your `Base` and set:
```python
from app.database import Base
target_metadata = Base.metadata
```

3. Generate migration:
```bash
alembic revision --autogenerate -m "create users and blogs"
alembic upgrade head
```

> Tip: For async engines or custom configs, adapt `env.py` as needed (see Alembic docs).

---

## 7) Run the app
```bash
uvicorn app.main:app --reload
# then visit: http://127.0.0.1:8000/docs
```

---

## 8) Quick curl examples
Create user:
```bash
curl -X POST "http://127.0.0.1:8000/users/" -H "Content-Type: application/json" -d '{"username":"alice","email":"alice@example.com"}'
```

Create blog:
```bash
curl -X POST "http://127.0.0.1:8000/blogs/?user_id=1" -H "Content-Type: application/json" -d '{"title":"Hello","content":"World"}'
```

Get user with blogs:
```bash
curl http://127.0.0.1:8000/users/1
```

---

## 9) Notes, tips & best practices
- Use **Alembic** for production migrations rather than `Base.metadata.create_all`.
- Prefer `joinedload` or `selectinload` when you need to avoid N+1 query problems.
- Keep `schemas` separate from `models` — Pydantic for I/O, SQLAlchemy for DB.
- Consider converting to **async SQLAlchemy** (SQLAlchemy 1.4+ async engines) for high-concurrency apps — then your DB layer and CRUD change shape (async sessions, async engine).
- Add input validation, authentication, and test coverage for endpoints.
