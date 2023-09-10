from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import schemas, db, models, oauth2

router = APIRouter(
    prefix="/api/v1/vote",
    tags=['Vote']
)

@router.post("", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote,
         db: Session = Depends(db.get_db),
         current_user: models.User = Depends(oauth2.get_current_user)):

    post = db.query(models.Post)\
             .filter(models.Post.id == vote.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post <{vote.post_id}> not found.")

    vote_query = db.query(models.Vote)\
                   .filter(models.Vote.post_id == vote.post_id,
                             models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()

    match vote.dir:
        case 1:
            if found_vote:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                    detail=f"User <{current_user.id}> already voted on Post <{vote.post_id}>")
            # Add a new vote
            new_vote = models.Vote(post_id = vote.post_id, user_id=current_user.id)
            db.add(new_vote)
            db.commit()
            return {"message" : f"User <{current_user.id}> voted on Post <{vote.post_id}>"}
        case 0:
            if not found_vote:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User <{current_user.id}> has not voted on Post <{vote.post_id}>")
            # Remove an existing vote
            vote_query.delete(synchronize_session=False)
            db.commit()
            return {"message" : f"User <{current_user.id}> removed vote on Post <{vote.post_id}>"}