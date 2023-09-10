from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, oauth2
from ..db import get_db

router = APIRouter(
    prefix="/api/v1/posts",
    tags=['Posts']
)

@router.get("",  response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db),
              current_user: models.User = Depends(oauth2.get_current_user),
              limit: int = 10,
              offset: int = 0,
              search: str = ""):
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes"))\
                .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)\
                .group_by(models.Post.id)\
                .filter(models.Post.title.contains(search))\
                .filter(models.Post.owner_id == current_user.id)\
                .limit(limit)\
                .offset(offset)\
                .all()
    return results

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate,
                db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostOut)
def get_post(id: str,
             db: Session = Depends(get_db)):
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes"))\
             .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)\
             .group_by(models.Post.id)\
             .filter(models.Post.id == id)\
             .first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail=f"404: Post <{id}> not found.")
    return post

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Post)
def update_post(id: int,
                updated_post: schemas.PostUpdate,
                db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post)\
                  .filter(models.Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail=f"404: Post <{id}> not found.")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                              detail=f"403: Unauthorized to update Post <{id}>.")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    db.refresh(post)
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: str,
                db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post)\
            .filter(models.Post.id == id)\
            .first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail=f"404: Post <{id}> not found.")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                              detail=f"403: Unauthorized to delete Post <{id}>.")
    db.delete(post)
    db.commit()