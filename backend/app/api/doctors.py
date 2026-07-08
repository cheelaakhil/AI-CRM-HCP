"""
Doctor/HCP API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.models.models import HCP
from app.schemas.schemas import HCPResponse, HCPCreate
from app.services.interaction_service import search_hcps

router = APIRouter(prefix="/api/doctors", tags=["Doctors"])


@router.get("", response_model=list[HCPResponse])
def list_doctors(
    q: Optional[str] = Query(None, description="Search query"),
    db: Session = Depends(get_db),
):
    """List or search doctors."""
    if q:
        return search_hcps(db, q)
    return db.query(HCP).limit(100).all()


@router.get("/{doctor_id}", response_model=HCPResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Get a single doctor by ID."""
    doctor = db.query(HCP).filter(HCP.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.post("", response_model=HCPResponse, status_code=201)
def create_doctor(data: HCPCreate, db: Session = Depends(get_db)):
    """Create a new doctor record."""
    doctor = HCP(**data.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor
