from sqlalchemy.orm import Session
from sqlalchemy import and_
from app import models, schemas
from typing import List, Optional


# -------------------------
# USER CRUD
# -------------------------

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str) -> models.User:
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# -------------------------
# GYM CRUD
# -------------------------

def create_gym(db: Session, gym: schemas.GymCreate, owner_id: int):
    db_gym = models.Gym(
        owner_id=owner_id,
        name=gym.name,
        address=gym.address,
        subscription_fee=gym.subscription_fee,
        trial_available=gym.trial_available,
        description=gym.description,
        location_lat=gym.location_lat,
        location_lng=gym.location_lng,
    )
    db.add(db_gym)
    db.commit()
    db.refresh(db_gym)
    return db_gym


def get_gyms(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    has_trial: Optional[bool] = None
):
    query = db.query(models.Gym)

    if location:
        query = query.filter(models.Gym.location.ilike(f"%{location}%"))
    if min_price is not None:
        query = query.filter(models.Gym.subscription_price >= min_price)
    if max_price is not None:
        query = query.filter(models.Gym.subscription_price <= max_price)
    if has_trial is not None:
        query = query.filter(models.Gym.has_trial == has_trial)

    return query.offset(skip).limit(limit).all()


def get_gym(db: Session, gym_id: int) -> Optional[models.Gym]:
    return db.query(models.Gym).filter(models.Gym.id == gym_id).first()



def update_gym(db: Session, gym_id: int, gym_update: schemas.GymUpdate) -> Optional[models.Gym]:
    db_gym = db.query(models.Gym).filter(models.Gym.id == gym_id).first()
    if not db_gym:
        return None

    update_data = gym_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_gym, key, value)

    db.commit()
    db.refresh(db_gym)
    return db_gym


def list_gyms(
    db: Session,
    max_fee: Optional[int] = None,
    trial: Optional[bool] = None,
    location: Optional[str] = None,
) -> List[models.Gym]:
    query = db.query(models.Gym)

    if max_fee:
        query = query.filter(models.Gym.subscription_fee <= max_fee)
    if trial is not None:
        query = query.filter(models.Gym.trial_available == trial)
    if location:
        query = query.filter(models.Gym.address.ilike(f"%{location}%"))

    return query.all()


# -------------------------
# TRAINER CRUD
# -------------------------

def add_trainer(db: Session, trainer: schemas.TrainerCreate, gym_id: int) -> models.Trainer:
    db_trainer = models.Trainer(
        gym_id=gym_id,
        name=trainer.name,
        specialty=trainer.specialty,
        fee=trainer.fee,
    )
    db.add(db_trainer)
    db.commit()
    db.refresh(db_trainer)
    return db_trainer


def list_trainers_by_gym(db: Session, gym_id: int) -> List[models.Trainer]:
    return db.query(models.Trainer).filter(models.Trainer.gym_id == gym_id).all()


# -------------------------
# TRIAL REQUEST CRUD
# -------------------------

def create_trial_request(db: Session, user_id: int, gym_id: int) -> models.TrialBooking:
    db_trial = models.TrialBooking(user_id=user_id, gym_id=gym_id)
    db.add(db_trial)
    db.commit()
    db.refresh(db_trial)
    return db_trial


def list_trial_requests_for_gym(db: Session, gym_id: int) -> List[models.TrialBooking]:
    return db.query(models.TrialBooking).filter(models.TrialBooking.gym_id == gym_id).all()


def update_trial_status(db: Session, trial_id: int, status: str) -> Optional[models.TrialBooking]:
    db_trial = db.query(models.TrialBooking).filter(models.TrialBooking.id == trial_id).first()
    if not db_trial:
        return None
    db_trial.status = status
    db.commit()
    db.refresh(db_trial)
    return db_trial



# Why this is production-ready:

# Uses exclude_unset=True in update_gym → supports partial updates (PATCH).
# Search filters (max_fee, trial, location) keep Stage 1 discovery feature simple but extendable.
# Separate CRUD functions for users, gyms, trainers, trial requests → modular.
# Returns ORM objects (to be converted into Pydantic schemas in routes).
# Avoids exposing sensitive data (password hashing handled outside CRUD).