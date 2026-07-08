"""
Five LangGraph-compatible tools for the AI CRM agent.

Tool 1: log_interaction — Extract entities from natural language and save to DB
Tool 2: edit_interaction — Find and modify an existing interaction
Tool 3: search_hcp — Search doctors by name, specialization, or hospital
Tool 4: interaction_history — Retrieve past interactions for a given doctor
Tool 5: followup_recommendation — AI-generated follow-up suggestions
"""

import json
from datetime import date, datetime
from typing import Optional
from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.models import HCP, Interaction, Material, SampleDistribution
from app.services.interaction_service import (
    create_interaction,
    get_interaction,
    update_interaction,
    search_hcps,
    get_hcp_by_name,
    get_interactions_by_hcp,
)
from app.schemas.schemas import InteractionCreate, InteractionUpdate, MaterialCreate, SampleCreate
from app.utils.llm import get_llm
from app.prompts.prompts import ENTITY_EXTRACTION_PROMPT, FOLLOWUP_RECOMMENDATION_PROMPT, EDIT_INTERACTION_PROMPT


def _get_db() -> Session:
    """Get a fresh database session for tool use."""
    return SessionLocal()


# ═══════════════════════════════════════════════════════════════════════
# Tool 1: Log Interaction
# ═══════════════════════════════════════════════════════════════════════

@tool
def log_interaction(user_input: str) -> str:
    """
    Extract structured medical interaction data from a natural language description
    and save it to the database. Use this when a pharmaceutical rep describes a meeting
    they had with a doctor.

    Args:
        user_input: Natural language description of the doctor interaction.

    Returns:
        JSON string with the saved interaction details and ID.
    """
    db = _get_db()
    try:
        # Step 1: Use LLM to extract entities
        llm = get_llm(temperature=0.0)
        extraction_prompt = ENTITY_EXTRACTION_PROMPT.format(
            user_input=user_input,
            today_date=date.today().isoformat(),
        )
        response = llm.invoke(extraction_prompt)
        
        # Step 2: Parse the extracted entities
        try:
            # Clean the response — strip markdown code fences if present
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]  # Remove first line
                content = content.rsplit("```", 1)[0]  # Remove last fence
            entities = json.loads(content)
        except json.JSONDecodeError:
            return json.dumps({
                "error": "Failed to extract structured data from the input.",
                "raw_response": response.content,
            })

        # Step 3: Find or handle the doctor
        doctor_name = entities.get("doctor_name")
        hcp = None
        if doctor_name:
            hcp = get_hcp_by_name(db, doctor_name)

        if not hcp and doctor_name:
            # Create a new HCP record
            hcp = HCP(name=doctor_name)
            db.add(hcp)
            db.flush()

        if not hcp:
            return json.dumps({
                "error": "Could not identify a doctor from the input. Please mention the doctor's name.",
                "extracted": entities,
            })

        # Step 4: Build the interaction
        # Parse date
        interaction_date = date.today()
        if entities.get("date"):
            try:
                interaction_date = datetime.strptime(entities["date"], "%Y-%m-%d").date()
            except ValueError:
                interaction_date = date.today()

        # Parse interaction type
        interaction_type = entities.get("interaction_type", "in_person")
        valid_types = ["in_person", "virtual", "phone", "email", "conference"]
        if interaction_type not in valid_types:
            interaction_type = "in_person"

        # Parse sentiment
        sentiment = entities.get("sentiment", "neutral")
        valid_sentiments = ["positive", "neutral", "negative"]
        if sentiment not in valid_sentiments:
            sentiment = "neutral"

        # Build materials
        materials = []
        for mat in entities.get("materials", []) or []:
            if isinstance(mat, dict) and mat.get("medicine_name"):
                materials.append(MaterialCreate(
                    medicine_name=mat["medicine_name"],
                    quantity=mat.get("quantity", 0),
                ))

        # Build samples
        samples = []
        for samp in entities.get("samples", []) or []:
            if isinstance(samp, dict) and samp.get("sample_name"):
                samples.append(SampleCreate(
                    sample_name=samp["sample_name"],
                    count=samp.get("count", 0),
                ))

        # Step 5: Save to database
        interaction_data = InteractionCreate(
            hcp_id=hcp.id,
            date=interaction_date,
            interaction_type=interaction_type,
            topics=entities.get("topics"),
            summary=entities.get("summary"),
            sentiment=sentiment,
            outcome=entities.get("outcome"),
            follow_up=entities.get("follow_up"),
            materials=materials,
            samples=samples,
        )
        interaction = create_interaction(db, interaction_data)

        return json.dumps({
            "success": True,
            "interaction_id": interaction.id,
            "doctor_name": hcp.name,
            "doctor_id": hcp.id,
            "date": interaction_date.isoformat(),
            "summary": entities.get("summary"),
            "sentiment": sentiment,
            "outcome": entities.get("outcome"),
            "follow_up": entities.get("follow_up"),
            "topics": entities.get("topics"),
            "products": entities.get("products", []),
            "materials": [m.model_dump() for m in materials],
            "samples": [s.model_dump() for s in samples],
            "interaction_type": interaction_type,
        })

    except Exception as e:
        return json.dumps({"error": f"Failed to log interaction: {str(e)}"})
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════
# Tool 2: Edit Interaction
# ═══════════════════════════════════════════════════════════════════════

@tool
def edit_interaction(user_input: str, interaction_id: Optional[int] = None) -> str:
    """
    Edit an existing interaction record based on natural language instructions.
    Use this when a user wants to modify details of a previously logged interaction.

    Args:
        user_input: Natural language description of the changes to make.
        interaction_id: Optional ID of the interaction to edit. If not provided,
                        the most recent interaction will be used.

    Returns:
        JSON string with the updated interaction details.
    """
    db = _get_db()
    try:
        # Step 1: Find the interaction
        if interaction_id:
            interaction = get_interaction(db, interaction_id)
        else:
            # Get the most recent interaction
            interaction = (
                db.query(Interaction)
                .order_by(Interaction.created_at.desc())
                .first()
            )

        if not interaction:
            return json.dumps({
                "error": "No interaction found to edit.",
                "suggestion": "Please specify an interaction ID or log a new interaction first.",
            })

        # Step 2: Use LLM to interpret the edit request
        current_data = {
            "id": interaction.id,
            "date": interaction.date.isoformat() if interaction.date else None,
            "topics": interaction.topics,
            "summary": interaction.summary,
            "sentiment": interaction.sentiment.value if interaction.sentiment else None,
            "outcome": interaction.outcome,
            "follow_up": interaction.follow_up,
            "interaction_type": interaction.interaction_type.value if interaction.interaction_type else None,
        }

        llm = get_llm(temperature=0.0)
        edit_prompt = EDIT_INTERACTION_PROMPT.format(
            user_input=user_input,
            current_interaction=json.dumps(current_data, indent=2),
        )
        response = llm.invoke(edit_prompt)

        # Step 3: Parse the changes
        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]
            changes = json.loads(content)
        except json.JSONDecodeError:
            return json.dumps({
                "error": "Could not interpret the edit request.",
                "raw_response": response.content,
            })

        # Step 4: Apply the changes
        update_data = InteractionUpdate(**changes)
        updated = update_interaction(db, interaction.id, update_data)

        if not updated:
            return json.dumps({"error": "Failed to update the interaction."})

        return json.dumps({
            "success": True,
            "interaction_id": updated.id,
            "changes_applied": changes,
            "message": f"Interaction #{updated.id} updated successfully.",
        })

    except Exception as e:
        return json.dumps({"error": f"Failed to edit interaction: {str(e)}"})
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════
# Tool 3: Search HCP
# ═══════════════════════════════════════════════════════════════════════

@tool
def search_hcp(query: str) -> str:
    """
    Search for healthcare professionals (doctors) by name, specialization,
    hospital, or city.

    Args:
        query: Search term to find doctors.

    Returns:
        JSON string with matching doctor records.
    """
    db = _get_db()
    try:
        results = search_hcps(db, query)

        if not results:
            return json.dumps({
                "results": [],
                "message": f"No doctors found matching '{query}'.",
                "suggestion": "Try a different search term or check the spelling.",
            })

        doctors = []
        for hcp in results:
            # Count interactions
            interaction_count = db.query(Interaction).filter(
                Interaction.hcp_id == hcp.id
            ).count()

            doctors.append({
                "id": hcp.id,
                "name": hcp.name,
                "specialization": hcp.specialization,
                "hospital": hcp.hospital,
                "city": hcp.city,
                "phone": hcp.phone,
                "email": hcp.email,
                "total_interactions": interaction_count,
            })

        return json.dumps({
            "results": doctors,
            "count": len(doctors),
            "message": f"Found {len(doctors)} doctor(s) matching '{query}'.",
        })

    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"})
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════
# Tool 4: Interaction History
# ═══════════════════════════════════════════════════════════════════════

@tool
def interaction_history(doctor_name: str, limit: int = 5) -> str:
    """
    Retrieve the interaction history for a specific doctor.
    Shows past meetings, summaries, sentiments, and outcomes.

    Args:
        doctor_name: The name of the doctor to look up history for.
        limit: Maximum number of interactions to return (default 5).

    Returns:
        JSON string with the interaction history.
    """
    db = _get_db()
    try:
        # Find the doctor
        hcp = get_hcp_by_name(db, doctor_name)
        if not hcp:
            return json.dumps({
                "error": f"No doctor found matching '{doctor_name}'.",
                "suggestion": "Try searching for the doctor first using the search tool.",
            })

        # Get interactions
        interactions = get_interactions_by_hcp(db, hcp.id, limit=limit)

        if not interactions:
            return json.dumps({
                "doctor": hcp.name,
                "interactions": [],
                "message": f"No interaction history found for {hcp.name}.",
            })

        history = []
        for ix in interactions:
            entry = {
                "id": ix.id,
                "date": ix.date.isoformat() if ix.date else None,
                "interaction_type": ix.interaction_type.value if ix.interaction_type else None,
                "topics": ix.topics,
                "summary": ix.summary,
                "sentiment": ix.sentiment.value if ix.sentiment else None,
                "outcome": ix.outcome,
                "follow_up": ix.follow_up,
                "materials": [
                    {"medicine_name": m.medicine_name, "quantity": m.quantity}
                    for m in ix.materials
                ],
                "samples": [
                    {"sample_name": s.sample_name, "count": s.count}
                    for s in ix.samples
                ],
            }
            history.append(entry)

        return json.dumps({
            "doctor": {
                "id": hcp.id,
                "name": hcp.name,
                "specialization": hcp.specialization,
                "hospital": hcp.hospital,
            },
            "interactions": history,
            "count": len(history),
            "message": f"Found {len(history)} interaction(s) with {hcp.name}.",
        })

    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve history: {str(e)}"})
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════
# Tool 5: Follow-up Recommendation
# ═══════════════════════════════════════════════════════════════════════

@tool
def followup_recommendation(doctor_name: str) -> str:
    """
    Generate AI-powered follow-up recommendations for a doctor based on
    their interaction history and sentiment trends.

    Args:
        doctor_name: The name of the doctor to generate recommendations for.

    Returns:
        JSON string with follow-up recommendations.
    """
    db = _get_db()
    try:
        # Find the doctor
        hcp = get_hcp_by_name(db, doctor_name)
        if not hcp:
            return json.dumps({
                "error": f"No doctor found matching '{doctor_name}'.",
                "suggestion": "Try searching for the doctor first.",
            })

        # Get recent interactions
        interactions = get_interactions_by_hcp(db, hcp.id, limit=5)

        if not interactions:
            return json.dumps({
                "doctor": hcp.name,
                "recommendations": "No interaction history available. Consider scheduling an introductory meeting.",
            })

        # Build history summary for the LLM
        history_text = ""
        latest = interactions[0]
        for ix in interactions:
            history_text += (
                f"- {ix.date}: {ix.summary or 'No summary'} "
                f"(Sentiment: {ix.sentiment.value if ix.sentiment else 'unknown'}, "
                f"Outcome: {ix.outcome or 'N/A'})\n"
            )

        # Use LLM for recommendations
        llm = get_llm(temperature=0.3)
        prompt = FOLLOWUP_RECOMMENDATION_PROMPT.format(
            doctor_name=hcp.name,
            specialization=hcp.specialization or "Unknown",
            summary=latest.summary or "No summary available",
            sentiment=latest.sentiment.value if latest.sentiment else "unknown",
            outcome=latest.outcome or "No outcome recorded",
            follow_up=latest.follow_up or "No follow-up scheduled",
            history=history_text,
        )
        response = llm.invoke(prompt)

        return json.dumps({
            "doctor": {
                "id": hcp.id,
                "name": hcp.name,
                "specialization": hcp.specialization,
            },
            "recommendations": response.content,
            "based_on_interactions": len(interactions),
            "latest_sentiment": latest.sentiment.value if latest.sentiment else "unknown",
        })

    except Exception as e:
        return json.dumps({"error": f"Failed to generate recommendations: {str(e)}"})
    finally:
        db.close()


# Export all tools for the graph
ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    search_hcp,
    interaction_history,
    followup_recommendation,
]
