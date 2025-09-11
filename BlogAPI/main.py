import uuid
from fastapi import FastAPI, Depends, HTTPException, status
from schemas import BlogResponse, BlogCreate, BlogBase, UserResponse, UserCreate
from database import get_db
import blog_crud 
from sqlalchemy.orm import Session
from utils import get_user_by_email, get_user_by_username, get_password_hash
import models
from sqlalchemy.exc import IntegrityError


app = FastAPI()

@app.post("/blog/create/", response_model=BlogResponse, status_code=status.HTTP_201_CREATED)
def create_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    return blog_crud.create_blog(db, blog)


@app.get("/blogs/", response_model=list[BlogResponse])
def get_blogs(limit:int = 10, start:int = 1, published:bool = True, db: Session = Depends(get_db)):
    return blog_crud.get_blogs(db, limit, start, published)


@app.get("/blog/{blog_id}/", response_model=BlogBase)
def get_blog(blog_id: str, db: Session = Depends(get_db)):
    try:
        blog_uuid = uuid.UUID(blog_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid blog_id format")
    db_blog = blog_crud.get_blog(db, blog_uuid)
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return db_blog


@app.delete("/blog/delete/{blog_id}/")
def delete_blog(blog_id: str, db: Session = Depends(get_db)):
    try:
        blog_uuid = uuid.UUID(blog_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid blog_id format")
    success = blog_crud.delete_blog(db, blog_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"message": "Blog deleted successfully"}


# -----------------------------------------------------User APIs------------------------------------------------
@app.post("/user/create/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check existing username
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    # Check existing email
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        db_user = models.User(
            username = user.username,
            email = user.email,
            full_name = user.full_name,
            hashed_password = get_password_hash(user.password)
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or Email already exists")


@app.get("/user/{user_id}/", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid blog_id format")
    db_user = db.query(models.User).filter(models.User.id == user_uuid).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return db_user