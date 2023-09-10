from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import schemas, models, oauth2
from ..db import get_db
from ..utils import verify

router = APIRouter(
    prefix="/api/v1",
    tags=['Authentication']
)

@router.post("/login", status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                              detail=f"401: Invalid Credentials.")
    correct_password = verify(user_credentials.password, user.password)
    if not correct_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                              detail=f"401: Invalid Credentials.")
    access_token = oauth2.create_access_token(data={"user_id" : user.id})
    return {"access_token" : access_token, "token_type" : "bearer"}