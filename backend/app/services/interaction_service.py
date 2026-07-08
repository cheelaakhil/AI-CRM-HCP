"""
Interaction service layer — business logic separated from route handlers.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Optional, List
from app.models.models import Interaction, Material, SampleDistribution, HCP
from app.schemas.schemas import InteractionCreate, InteractionUpdate


def create_interaction(db: Session, data: InteractionCreate) -> Interaction:
    """Create a new interaction with optional materials and samples."""
    interaction = Interaction(
        hcp_id=data.hcp_id,
        date=data.date,
        interaction_type=data.interaction_type,
        topics=data.topics,
        summary=data.summary,
        sentiment=data.sentiment,
        outcome=data.outcome,
        follow_up=data.follow_up,
    )
    db.add(interaction)
    db.flush()  # Get the ID before adding children

    # Add materials
    if data.materials:
        for mat in data.materials:
            material = Material(
                interaction_id=interaction.id,
                medicine_name=mat.medicine_name,
                quantity=mat.quantity,
            )
            db.add(material)

    # Add samples
    if data.samples:
        for samp in data.samples:
            sample = SampleDistribution(
                interaction_id=interaction.id,
                sample_name=samp.sample_name,
                count=samp.count,
            )
            db.add(sample)

    db.commit()
    db.refresh(interaction)
    return interaction


def get_interaction(db: Session, interaction_id: int) -> Optional[Interaction]:
    """Get a single interaction by ID with related data."""
    return (
        db.query(Interaction)
        .options(
            joinedload(Interaction.hcp),
            joinedload(Interaction.materials),
            joinedload(Interaction.samples),
        )
        .filter(Interaction.id == interaction_id)
        .first()
    )


def get_interactions(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    hcp_id: Optional[int] = None,
) -> tuple[List[Interaction], int]:
    """List interactions with optional HCP filter and pagination."""
    query = db.query(Interaction).options(
        joinedload(Interaction.hcp),
        joinedload(Interaction.materials),
        joinedload(Interaction.samples),
    )

    if hcp_id:
        query = query.filter(Interaction.hcp_id == hcp_id)

    total = db.query(Interaction).count()
    interactions = query.order_by(desc(Interaction.created_at)).offset(skip).limit(limit).all()
    return interactions, total


def update_interaction(db: Session, interaction_id: int, data: InteractionUpdate) -> Optional[Interaction]:
    """Update an existing interaction."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # Handle materials separately
    if "materials" in update_data and update_data["materials"] is not None:
        # Clear existing materials
        db.query(Material).filter(Material.interaction_id == interaction_id).delete()
        for mat in update_data.pop("materials"):
            material = Material(
                interaction_id=interaction_id,
                medicine_name=mat["medicine_name"],
                quantity=mat.get("quantity", 0),
            )
            db.add(material)
    else:
        update_data.pop("materials", None)

    # Handle samples separately
    if "samples" in update_data and update_data["samples"] is not None:
        db.query(SampleDistribution).filter(SampleDistribution.interaction_id == interaction_id).delete()
        for samp in update_data.pop("samples"):
            sample = SampleDistribution(
                interaction_id=interaction_id,
                sample_name=samp["sample_name"],
                count=samp.get("count", 0),
            )
            db.add(sample)
    else:
        update_data.pop("samples", None)

    # Update scalar fields
    for key, value in update_data.items():
        setattr(interaction, key, value)

    db.commit()
    db.refresh(interaction)
    return interaction


def delete_interaction(db: Session, interaction_id: int) -> bool:
    """Delete an interaction by ID."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        return False
    db.delete(interaction)
    db.commit()
    return True


# ─── HCP helpers (used by tools) ─────────────────────────────────────

def search_hcps(db: Session, query: str) -> List[HCP]:
    """Search doctors by name, specialization, or hospital."""
    pattern = f"%{query}%"
    return (
        db.query(HCP)
        .filter(
            (HCP.name.ilike(pattern))
            | (HCP.specialization.ilike(pattern))
            | (HCP.hospital.ilike(pattern))
            | (HCP.city.ilike(pattern))
        )
        .limit(20)
        .all()
    )


def get_hcp_by_name(db: Session, name: str) -> Optional[HCP]:
    """Find a doctor by approximate name match."""
    pattern = f"%{name}%"
    return db.query(HCP).filter(HCP.name.ilike(pattern)).first()


def get_interactions_by_hcp(db: Session, hcp_id: int, limit: int = 10) -> List[Interaction]:
    """Get recent interactions for a specific doctor."""
    return (
        db.query(Interaction)
        .options(
            joinedload(Interaction.materials),
            joinedload(Interaction.samples),
        )
        .filter(Interaction.hcp_id == hcp_id)
        .order_by(desc(Interaction.date))
        .limit(limit)
        .all()
    )
