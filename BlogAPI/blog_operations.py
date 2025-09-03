# CRUD operations for Blog model
from sqlalchemy.orm import Session
import models, schemas


def get_blogs(db: Session):
    return db.query(models.Blog).all()


def get_blog(db: Session, blog_id):
    return db.query(models.Blog).filter(models.Blog.id == blog_id).first()


def create_blog(db: Session, blog: schemas.BlogCreate):
    db_blog = models.Blog(
        title=blog.title,
        body=blog.body,
        published=blog.published,
    )
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog


def delete_blog(db: Session, blog_id):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if blog:
        db.delete(blog)
        db.commit()
        return True
    return False
