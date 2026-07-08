"""
SQLAlchemy ORM models for the AI-CRM-HCP application.
"""

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.database.database import Base
import enum


class SentimentEnum(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class InteractionTypeEnum(str, enum.Enum):
    IN_PERSON = "in_person"
    VIRTUAL = "virtual"
    PHONE = "phone"
    EMAIL = "email"
    CONFERENCE = "conference"


class HCP(Base):
    """Healthcare Professional (Doctor) table."""
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    specialization = Column(String(200), nullable=True)
    hospital = Column(String(300), nullable=True)
    city = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)

    # Relationships
    interactions = relationship("Interaction", back_populates="hcp", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HCP(id={self.id}, name='{self.name}', specialization='{self.specialization}')>"


class Interaction(Base):
    """Interaction log between a medical rep and a doctor."""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False, index=True)
    date = Column(Date, default=date.today, nullable=False)
    interaction_type = Column(
        SQLEnum(InteractionTypeEnum),
        default=InteractionTypeEnum.IN_PERSON,
        nullable=False
    )
    topics = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    sentiment = Column(
        SQLEnum(SentimentEnum),
        default=SentimentEnum.NEUTRAL,
        nullable=False
    )
    outcome = Column(Text, nullable=True)
    follow_up = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    hcp = relationship("HCP", back_populates="interactions")
    materials = relationship("Material", back_populates="interaction", cascade="all, delete-orphan")
    samples = relationship("SampleDistribution", back_populates="interaction", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Interaction(id={self.id}, hcp_id={self.hcp_id}, date={self.date})>"


class Material(Base):
    """Materials/medicines discussed during an interaction."""
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=False, index=True)
    medicine_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=0)

    # Relationships
    interaction = relationship("Interaction", back_populates="materials")

    def __repr__(self):
        return f"<Material(id={self.id}, medicine='{self.medicine_name}', qty={self.quantity})>"


class SampleDistribution(Base):
    """Samples distributed to a doctor during an interaction."""
    __tablename__ = "sample_distributions"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=False, index=True)
    sample_name = Column(String(200), nullable=False)
    count = Column(Integer, default=0)

    # Relationships
    interaction = relationship("Interaction", back_populates="samples")

    def __repr__(self):
        return f"<SampleDistribution(id={self.id}, sample='{self.sample_name}', count={self.count})>"
