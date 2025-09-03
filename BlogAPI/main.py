from fastapi import FastAPI, Depends, HTTPException
from schemas import BlogResponse, BlogCreate
from database import get_db
import blog_operations 
from sqlalchemy.orm import Session


app = FastAPI()

@app.post("/blog/create/", response_model=BlogResponse)
def create_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    return blog_operations.create_blog(db, blog)


@app.get("/blogs/", response_model=list[BlogResponse])
def get_blogs(db: Session = Depends(get_db)):
    return blog_operations.get_blogs(db)


@app.get("/blog/{blog_id}/", response_model=BlogResponse)
def get_blog(blog_id: str, db: Session = Depends(get_db)):
    db_blog = blog_operations.get_blog(db, blog_id)
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return db_blog


@app.delete("/blog/delete/{blog_id}/")
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    success = blog_operations.delete_blog(db, blog_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"message": "Blog deleted successfully"}