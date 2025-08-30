# app/routes/trials.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas, crud, models
from app.db import get_db
from app.utils import get_current_user  # JWT-based auth
from app.models import TrialStatus

router = APIRouter(prefix="/trials", tags=["Trials"])

@router.post("/", response_model=schemas.Trial)
def book_trial(
    trial: schemas.TrialBookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Book a trial session for a gym.
    - User must be authenticated
    - Prevents duplicate active bookings
    """

    # Check if gym exists
    gym = crud.get_gym(db=db, gym_id=trial.gym_id)
    if not gym:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym not found"
        )

    # Prevent multiple active trial bookings for the same gym
    existing_trial = (
        db.query(models.TrialBooking)
        .filter(
            models.TrialBooking.gym_id == trial.gym_id,
            models.TrialBooking.user_id == current_user.id,
            models.TrialBooking.status == "pending"
        )
        .first()
    )
    if existing_trial:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending trial booking for this gym"
        )

    # Create trial booking
    trial_booking = models.TrialBooking(
        user_id=current_user.id,
        gym_id=trial.gym_id,
        scheduled_at=trial.scheduled_at,   # ✅ now stored
        status="pending"  # default status
    )
    db.add(trial_booking)
    db.commit()
    db.refresh(trial_booking)

    return trial_booking


@router.put("/{trial_id}/status", response_model=schemas.Trial)
def update_trial_status(
    trial_id: int,
    request: schemas.TrialStatusUpdate,  # 👈 take body as schema
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update trial booking status (approve, completed, cancelled).
    Only gym owners or admins can update.
    """

    # Get trial booking
    trial = db.query(models.TrialBooking).filter(models.TrialBooking.id == trial_id).first()
    if not trial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trial booking not found"
        )

    # Only gym owner or admin can update status
    if trial.gym.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this trial booking"
        )

    allowed_statuses = {TrialStatus.pending, TrialStatus.accepted, TrialStatus.rejected}
    if request.status_update not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status must be one of {allowed_statuses}"
        )

    trial.status = request.status_update
    db.commit()
    db.refresh(trial)

    return trial


# Key Features & Security

# JWT Auth (get_current_user) → Ensures only logged-in users can book trials.
# Validation for duplicates → Users cannot spam multiple pending trial requests at the same gym.

# Ownership check → Only gym owners/admins can change trial statuses.
# Clear status flow:
    # pending → initial booking
    # approved → gym accepts
    # completed → user attended
    # cancelled → user/gym cancels
# Future Scalability → Easy to extend with notifications, time slots, or payments.