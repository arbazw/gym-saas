# app/models.py

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, Float,
    Enum, ForeignKey
)
from sqlalchemy.orm import relationship, declarative_base
import enum


Base = declarative_base()


# -------------------------
# ENUMS
# -------------------------

class UserRole(enum.Enum):
    seeker = "seeker"
    gym_owner = "gym_owner"
    customer = "customer"
    admin = "admin"


class TrialStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


# -------------------------
# USER MODEL
# -------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.seeker, nullable=False)

    gyms = relationship("Gym", back_populates="owner", cascade="all, delete-orphan")
    trial_bookings = relationship("TrialBooking", back_populates="user", cascade="all, delete-orphan")


# -------------------------
# GYM MODEL
# -------------------------

class Gym(Base):
    __tablename__ = "gyms"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    subscription_fee = Column(Integer, nullable=False)
    trial_available = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="gyms")
    trainers = relationship("Trainer", back_populates="gym", cascade="all, delete-orphan")
    trial_bookings = relationship("TrialBooking", back_populates="gym", cascade="all, delete-orphan")


# -------------------------
# TRAINER MODEL
# -------------------------

class Trainer(Base):
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    specialty = Column(String, nullable=True)
    fee = Column(Integer, nullable=True)

    gym = relationship("Gym", back_populates="trainers")


# -------------------------
# TRIAL BOOKING MODEL
# -------------------------

class TrialBooking(Base):
    __tablename__ = "trial_bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    gym_id = Column(Integer, ForeignKey("gyms.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(TrialStatus), default=TrialStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trial_bookings")
    gym = relationship("Gym", back_populates="trial_bookings")








# Why this design is strong:

# Enums (UserRole, TrialStatus) → ensures valid roles/status only.
# Relationships:
    # User → Gym (owner manages gyms).
    # Gym → Trainer (trainers belong to gym).
    # User → TrialBooking → Gym (seeker books a trial).
# Cascades → if a gym is deleted, trainers and trial requests are auto-deleted.
# Indexes → email, id, ForeignKey fields optimized for queries.
# Timestamps → track creation dates for analytics.