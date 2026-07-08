"""
Seed script — populates the database with sample doctors and interactions.
Run with: python -m app.utils.seed
"""

from datetime import date, timedelta
from app.database.database import SessionLocal, init_db
from app.models.models import HCP, Interaction, Material, SampleDistribution, SentimentEnum, InteractionTypeEnum


SAMPLE_DOCTORS = [
    {"name": "Dr. Rajesh Sharma", "specialization": "Endocrinology", "hospital": "Apollo Hospital", "city": "Mumbai", "phone": "+91-9876543210", "email": "rajesh.sharma@apollo.com"},
    {"name": "Dr. Priya Patel", "specialization": "Cardiology", "hospital": "Fortis Hospital", "city": "Delhi", "phone": "+91-9876543211", "email": "priya.patel@fortis.com"},
    {"name": "Dr. Anil Kumar", "specialization": "Orthopedics", "hospital": "Max Healthcare", "city": "Bangalore", "phone": "+91-9876543212", "email": "anil.kumar@max.com"},
    {"name": "Dr. Sneha Reddy", "specialization": "Dermatology", "hospital": "Manipal Hospital", "city": "Hyderabad", "phone": "+91-9876543213", "email": "sneha.reddy@manipal.com"},
    {"name": "Dr. Vikram Singh", "specialization": "Neurology", "hospital": "AIIMS", "city": "Delhi", "phone": "+91-9876543214", "email": "vikram.singh@aiims.com"},
    {"name": "Dr. Meera Joshi", "specialization": "Pediatrics", "hospital": "Rainbow Hospital", "city": "Chennai", "phone": "+91-9876543215", "email": "meera.joshi@rainbow.com"},
    {"name": "Dr. Sanjay Gupta", "specialization": "Oncology", "hospital": "Tata Memorial", "city": "Mumbai", "phone": "+91-9876543216", "email": "sanjay.gupta@tata.com"},
    {"name": "Dr. Kavita Desai", "specialization": "Gynecology", "hospital": "Lilavati Hospital", "city": "Mumbai", "phone": "+91-9876543217", "email": "kavita.desai@lilavati.com"},
    {"name": "Dr. Amit Verma", "specialization": "Psychiatry", "hospital": "Medanta Hospital", "city": "Gurugram", "phone": "+91-9876543218", "email": "amit.verma@medanta.com"},
    {"name": "Dr. Nisha Agarwal", "specialization": "Endocrinology", "hospital": "Kokilaben Hospital", "city": "Mumbai", "phone": "+91-9876543219", "email": "nisha.agarwal@kokilaben.com"},
    {"name": "Dr. Ravi Menon", "specialization": "Pulmonology", "hospital": "Narayana Health", "city": "Bangalore", "phone": "+91-9876543220", "email": "ravi.menon@narayana.com"},
    {"name": "Dr. Sunita Rao", "specialization": "Rheumatology", "hospital": "Care Hospital", "city": "Hyderabad", "phone": "+91-9876543221", "email": "sunita.rao@care.com"},
]

SAMPLE_INTERACTIONS = [
    {
        "hcp_idx": 0,
        "date_offset": -5,
        "interaction_type": InteractionTypeEnum.IN_PERSON,
        "topics": "Diabetes management, GlucoCare efficacy",
        "summary": "Discussed GlucoCare for Type 2 diabetes patients. Dr. Sharma was impressed with the clinical trial data showing 15% better HbA1c reduction. Concerned about insurance coverage for patients.",
        "sentiment": SentimentEnum.POSITIVE,
        "outcome": "Doctor will start prescribing for new patients",
        "follow_up": "Bring updated insurance formulary next Tuesday",
        "materials": [{"medicine_name": "GlucoCare 500mg", "quantity": 2}],
        "samples": [{"sample_name": "GlucoCare 500mg Starter Pack", "count": 5}],
    },
    {
        "hcp_idx": 1,
        "date_offset": -3,
        "interaction_type": InteractionTypeEnum.IN_PERSON,
        "topics": "Hypertension, CardioShield, beta-blockers",
        "summary": "Presented CardioShield for resistant hypertension. Dr. Patel already uses competitor products but showed interest in our combination therapy approach.",
        "sentiment": SentimentEnum.NEUTRAL,
        "outcome": "Requested peer-reviewed studies for comparison",
        "follow_up": "Send clinical comparison studies by email",
        "materials": [{"medicine_name": "CardioShield 10mg", "quantity": 1}],
        "samples": [{"sample_name": "CardioShield 10mg", "count": 3}],
    },
    {
        "hcp_idx": 0,
        "date_offset": -15,
        "interaction_type": InteractionTypeEnum.VIRTUAL,
        "topics": "Insulin resistance, new research",
        "summary": "Virtual meeting to discuss latest research on insulin resistance. Shared recent publication data. Dr. Sharma suggested a CME session for his department.",
        "sentiment": SentimentEnum.POSITIVE,
        "outcome": "Planning CME session",
        "follow_up": "Coordinate with hospital for CME date",
        "materials": [{"medicine_name": "InsulinPro XR", "quantity": 1}],
        "samples": [],
    },
    {
        "hcp_idx": 2,
        "date_offset": -7,
        "interaction_type": InteractionTypeEnum.IN_PERSON,
        "topics": "Pain management, OrthoFlex",
        "summary": "Introduced OrthoFlex for post-surgical pain management. Dr. Kumar raised concerns about the side effect profile compared to existing NSAIDs.",
        "sentiment": SentimentEnum.NEGATIVE,
        "outcome": "Doctor not convinced, prefers current protocol",
        "follow_up": "Prepare side-effect comparison data",
        "materials": [{"medicine_name": "OrthoFlex 200mg", "quantity": 1}],
        "samples": [{"sample_name": "OrthoFlex 200mg", "count": 2}],
    },
    {
        "hcp_idx": 4,
        "date_offset": -2,
        "interaction_type": InteractionTypeEnum.IN_PERSON,
        "topics": "Migraine treatment, NeuroCalm",
        "summary": "Discussed NeuroCalm for chronic migraine prevention. Dr. Singh was very interested in the once-monthly dosing schedule. Wants to trial with 5 patients.",
        "sentiment": SentimentEnum.POSITIVE,
        "outcome": "Will start trial with 5 patients",
        "follow_up": "Provide patient enrollment forms by Friday",
        "materials": [{"medicine_name": "NeuroCalm 70mg", "quantity": 3}],
        "samples": [{"sample_name": "NeuroCalm 70mg Injection", "count": 5}],
    },
]


def seed_database():
    """Populate the database with sample data."""
    init_db()
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_count = db.query(HCP).count()
        if existing_count > 0:
            print(f"[SKIP] Database already has {existing_count} doctors. Skipping seed.")
            return

        # Insert doctors
        doctors = []
        for doc_data in SAMPLE_DOCTORS:
            doctor = HCP(**doc_data)
            db.add(doctor)
            doctors.append(doctor)

        db.flush()
        print(f"[OK] Inserted {len(doctors)} doctors")

        # Insert interactions
        for ix_data in SAMPLE_INTERACTIONS:
            hcp = doctors[ix_data["hcp_idx"]]
            interaction = Interaction(
                hcp_id=hcp.id,
                date=date.today() + timedelta(days=ix_data["date_offset"]),
                interaction_type=ix_data["interaction_type"],
                topics=ix_data["topics"],
                summary=ix_data["summary"],
                sentiment=ix_data["sentiment"],
                outcome=ix_data["outcome"],
                follow_up=ix_data["follow_up"],
            )
            db.add(interaction)
            db.flush()

            # Add materials
            for mat in ix_data.get("materials", []):
                db.add(Material(
                    interaction_id=interaction.id,
                    medicine_name=mat["medicine_name"],
                    quantity=mat["quantity"],
                ))

            # Add samples
            for samp in ix_data.get("samples", []):
                db.add(SampleDistribution(
                    interaction_id=interaction.id,
                    sample_name=samp["sample_name"],
                    count=samp["count"],
                ))

        db.commit()
        print(f"[OK] Inserted {len(SAMPLE_INTERACTIONS)} interactions with materials and samples")
        print("[OK] Seed completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
