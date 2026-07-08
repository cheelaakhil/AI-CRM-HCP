"""
Interaction CRUD API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.schemas.schemas import (
    InteractionCreate, InteractionUpdate, InteractionResponse,
    InteractionListResponse,
)
from app.services.interaction_service import (
    create_interaction,
    get_interaction,
    get_interactions,
    update_interaction,
    delete_interaction,
)

router = APIRouter(prefix="/api/interactions", tags=["Interactions"])


@router.post("", response_model=InteractionResponse, status_code=201)
def create_new_interaction(data: InteractionCreate, db: Session = Depends(get_db)):
    """Create a new interaction record via the traditional form."""
    interaction = create_interaction(db, data)
    return interaction


@router.get("", response_model=InteractionListResponse)
def list_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    hcp_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List all interactions with optional filtering."""
    interactions, total = get_interactions(db, skip=skip, limit=limit, hcp_id=hcp_id)
    return InteractionListResponse(interactions=interactions, total=total)


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_single_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """Get a single interaction by ID."""
    interaction = get_interaction(db, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.put("/{interaction_id}", response_model=InteractionResponse)
def update_existing_interaction(
    interaction_id: int,
    data: InteractionUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing interaction."""
    interaction = update_interaction(db, interaction_id, data)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.delete("/{interaction_id}", status_code=204)
def delete_existing_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """Delete an interaction."""
    success = delete_interaction(db, interaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return None
