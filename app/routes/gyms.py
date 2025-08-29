# app/routes/gyms.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, schemas, models
from app.db import get_db
from app.utils import get_current_user
from app.models import UserRole

router = APIRouter(prefix="/gyms", tags=["Gyms"])

# --------------------------
# Create Gym (Gym Owner Only)
# --------------------------
@router.post("/", response_model=schemas.GymOut)
def create_gym(
    gym: schemas.GymCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.gym_owner, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Not authorized to create gyms")
    
    return crud.create_gym(db=db, gym=gym, owner_id=current_user.id)


# --------------------------
# Get Gym by ID
# --------------------------
@router.get("/{gym_id}", response_model=schemas.GymOut)
def get_gym(
    gym_id: int,
    db: Session = Depends(get_db)
):
    gym = crud.get_gym(db, gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")
    return gym


# --------------------------
# Get All Gyms with Filters
# --------------------------
@router.get("/", response_model=List[schemas.GymOut])
def list_gyms(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    location: Optional[str] = Query(None, description="Filter by location"),
    min_price: Optional[float] = Query(None, description="Min subscription price"),
    max_price: Optional[float] = Query(None, description="Max subscription price"),
    has_trial: Optional[bool] = Query(None, description="Filter gyms offering trial")
):
    gyms = crud.get_gyms(
        db,
        skip=skip,
        limit=limit,
        location=location,
        min_price=min_price,
        max_price=max_price,
        has_trial=has_trial,
    )
    return gyms

# --------------------------
# Update Gym (Gym Owner/Admin Only)
# --------------------------
@router.put("/{gym_id}", response_model=schemas.GymOut)
def update_gym(
    gym_id: int,
    gym_update: schemas.GymUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    gym = crud.get_gym(db, gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    # only owner or admin can update
    if current_user.role not in [UserRole.gym_owner, UserRole.admin] or gym.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this gym")

    return crud.update_gym(db, gym_id, gym_update)


# --------------------------
# Delete Gym (Owner/Admin Only)
# --------------------------
@router.delete("/{gym_id}")
def delete_gym(
    gym_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    gym = crud.get_gym(db, gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    if current_user.role not in [UserRole.gym_owner, UserRole.admin] or gym.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this gym")

    crud.delete_gym(db, gym_id)
    return {"msg": "Gym deleted successfully"}




# What’s included here:

# create_gym: only gym_owner or admin can create a gym.
# list_gyms: filter gyms by location, price range, and trial availability.
# update_gym: gym owner can only update their own gym, admin can update any.
# delete_gym: same rule as update.
# Secure role-based checks using get_current_user.
# Pagination with skip & limit.