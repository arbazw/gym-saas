# app/utils.py

from datetime import datetime, timedelta
import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import get_db
from app import crud, models

# -----------------------------
# Security Config
# -----------------------------
# Always override SECRET_KEY via env in production
SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION_please_use_env")
ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Password hashing (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 bearer (used by /users/login token endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# -----------------------------
# Password Helpers
# -----------------------------
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# -----------------------------
# JWT Helpers
# -----------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT. `data` should contain a 'sub' (subject) field,
    typically the user's email.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# -----------------------------
# Current User Dependency
# -----------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Decodes JWT, fetches user from DB, and returns the ORM user.
    Raises 401 if token is invalid/expired or user not found.
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exc
    return user

# -----------------------------
# Authorization Helpers
# -----------------------------
def ensure_role_owner(user: models.User) -> None:
    """
    Ensures the user has 'owner' role for actions that only gym owners can perform.
    """
    if getattr(user, "role", None) != models.UserRole.owner:
        raise HTTPException(status_code=403, detail="Only gym owners can perform this action")

def ensure_gym_ownership(gym: models.Gym, user: models.User) -> None:
    """
    Ensures the given user is the owner of the provided gym.
    """
    if gym.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this gym")

def ensure_owner_and_ownership(gym: models.Gym, user: models.User) -> None:
    """
    Convenience check for routes that require the caller to be an owner
    AND the owner of this specific gym.
    """
    ensure_role_owner(user)
    ensure_gym_ownership(gym, user)
