from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from config import Base

class User(Base):
    __tablename__ = "USER"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    age = Column(Integer)
    gender = Column(Boolean)
    weight = Column(Float)
    height = Column(Float)
    bmi = Column(Float)
    drinking_status = Column(Boolean)
    smoking_status = Column(Boolean)
    obesity_status = Column(Integer)
    fatigue_status = Column(Boolean)

    # Relationships
    details = relationship("Detail", back_populates="user", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")
    tvs = relationship("TV", back_populates="user", cascade="all, delete-orphan")


class Detail(Base):
    __tablename__ = "DETAIL"

    detail_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("USER.user_id"), nullable=False)
    systolic_bp = Column(Integer)
    diastolic_bp = Column(Integer)
    heart_rate = Column(Integer)
    daily_steps = Column(Integer)
    cholesterol_status = Column(Boolean)
    daily_sleep = Column(Float)
    hypertension_status = Column(Boolean)

    user = relationship("User", back_populates="details")


class Video(Base):
    __tablename__ = "VIDEO"

    video_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("USER.user_id"),autoincrement=True, nullable=False)
    title = Column(String(255))
    video_length = Column(Integer)
    viewing_time = Column(Integer, default=0)
    category = Column(String(50))

    user = relationship("User", back_populates="videos")


class TV(Base):
    __tablename__ = "TV"

    tv_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("USER.user_id"), nullable=False)

    user = relationship("User", back_populates="tvs")
