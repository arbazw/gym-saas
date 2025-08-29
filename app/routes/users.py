# app/routes/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app import schemas, crud
from app.db import get_db
from app.utils import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["Users"]) # we can remove this if we don't want /users prefix

# -------------------------
# Register
# -------------------------
@router.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user.password)

    # ✅ pass schema + hash correctly
    db_user = crud.create_user(db, user=user, hashed_password=hashed_password)

    return db_user


# -------------------------
# Login (JWT Token)
# -------------------------
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# -------------------------
# Get Current User Profile
# -------------------------
@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user=Depends(get_current_user)):
    return current_user






# Key Security Features

# JWT Auth with OAuth2PasswordBearer.
# Password hashing with bcrypt (in utils.py).
# Token expiry (default: 1 hour).
# Secure login via OAuth2PasswordRequestForm.
# Protected routes using Depends(get_current_user).