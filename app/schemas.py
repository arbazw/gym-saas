# app/schemas.py

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

from app.models import UserRole


# -------------------------
# AUTH / TOKEN SCHEMAS
# -------------------------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -------------------------
# USER SCHEMAS
# -------------------------

class UserBase(BaseModel):
    name: str
    email: EmailStr


# class UserCreate(UserBase):
#     email: str
#     password: str
#     role: Optional[str] = "seeker"   # "seeker" or "gym_owner"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole # Add this line

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True


# -------------------------
# TRAINER SCHEMAS
# -------------------------

class TrainerBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    fee: Optional[int] = None


class TrainerCreate(TrainerBase):
    pass


class TrainerOut(TrainerBase):
    id: int
    name: str

    class Config:
        orm_mode = True


# -------------------------
# GYM SCHEMAS
# -------------------------

class GymBase(BaseModel):
    name: str
    address: str
    subscription_fee: int
    trial_available: Optional[bool] = False
    description: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None


class GymCreate(GymBase):
    pass


class GymUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    subscription_fee: Optional[int] = None
    trial_available: Optional[bool] = None
    description: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None


class GymOut(GymBase):
    id: int
    owner_id: int
    created_at: datetime
    trainers: List[TrainerOut] = []

    class Config:
        orm_mode = True


# -------------------------
# TRIAL BOOKING SCHEMAS
# -------------------------

class TrialBookingBase(BaseModel):
    gym_id: int


class TrialBookingCreate(TrialBookingBase):
    pass


class TrialBookingOut(TrialBookingBase):
    id: int
    user_id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


# ---------------- Trials ----------------

class TrialBase(BaseModel):
    user_id: int
    gym_id: int
    scheduled_at: datetime

class TrialCreate(TrialBase):
    pass

class Trial(TrialBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True




# Key Points About This Design:

# UserCreate vs UserOut → avoids returning password hash in responses.
# Gym schemas → GymOut includes a list of trainers (nested schema).
# Update schemas (GymUpdate) → all fields optional, useful for PATCH/PUT.
# Trial Requests → separated Create (user sends request) vs Out (response with status).
# orm_mode = True ensures compatibility with SQLAlchemy ORM objects.

# ----------------------------------------------------------
# Summary
# ----------------------------------------------------------

# This schema set is production-grade and covers:

# Authentication (UserCreate/Login/Out).
# Gym management (GymCreate/Update/Out).
# Trainer management (TrainerCreate/Out).
# Trial bookings (TrialBookingCreate/Out).