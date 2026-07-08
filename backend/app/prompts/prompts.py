"""
Prompt templates for the AI CRM agent.
"""

SYSTEM_PROMPT = """You are an AI CRM assistant for pharmaceutical sales representatives.
Your job is to help medical reps log, manage, and analyze their interactions with healthcare professionals (HCPs/doctors).

You can help with:
1. **Log Interaction** — Extract structured data from natural language descriptions of doctor meetings
2. **Edit Interaction** — Modify existing interaction records
3. **Search HCP** — Find doctors by name, specialization, or hospital
4. **Interaction History** — Show past meetings with a specific doctor
5. **Follow-up Recommendation** — Suggest next steps based on interaction context

Guidelines:
- Always extract structured information when a user describes a meeting
- Never invent facts — only use information provided by the user
- Be concise and professional
- When you extract entities, always confirm with the user what you found
- Dates should be interpreted relative to today's date
- If the user mentions a doctor name, try to match it to existing records
"""

INTENT_CLASSIFICATION_PROMPT = """Analyze the following user message and classify the intent into one of these categories:

1. "log_interaction" — The user is describing a meeting/interaction they had with a doctor and wants to log it
2. "edit_interaction" — The user wants to modify or update an existing interaction record
3. "search_hcp" — The user wants to find/search for a doctor
4. "interaction_history" — The user wants to see past interactions with a doctor
5. "followup_recommendation" — The user wants suggestions for next steps with a doctor
6. "general" — General conversation, greeting, or question that doesn't fit the above

User message: {user_input}

Conversation context: {conversation_history}

Respond with ONLY the intent category name (e.g., "log_interaction"). Nothing else."""

ENTITY_EXTRACTION_PROMPT = """Extract structured information from this medical interaction description.

User message: {user_input}

Today's date is: {today_date}

Extract the following fields (use null if not mentioned):
- doctor_name: The name of the doctor/HCP
- products: List of medicines/products discussed
- sentiment: "positive", "neutral", or "negative" based on doctor's reaction
- summary: A concise summary of the interaction
- outcome: The result or outcome of the meeting
- follow_up: Any follow-up actions or next meeting date
- samples: List of samples given (each with sample_name and count)
- materials: List of materials/medicines discussed (each with medicine_name and quantity)
- topics: Key topics discussed
- interaction_type: "in_person", "virtual", "phone", "email", or "conference"
- date: The date of the interaction (interpret relative dates like "today", "yesterday", "last Tuesday" relative to today's date)

Respond with ONLY valid JSON. No other text. Example format:
{{
    "doctor_name": "Dr. Smith",
    "products": ["MedicineA", "MedicineB"],
    "sentiment": "positive",
    "summary": "Discussed MedicineA efficacy...",
    "outcome": "Doctor interested in prescribing",
    "follow_up": "Next Tuesday",
    "samples": [{{"sample_name": "MedicineA", "count": 2}}],
    "materials": [{{"medicine_name": "MedicineA", "quantity": 1}}],
    "topics": "Diabetes management, drug efficacy",
    "interaction_type": "in_person",
    "date": "2026-07-08"
}}"""

FOLLOWUP_RECOMMENDATION_PROMPT = """Based on the following interaction details, provide follow-up recommendations for the pharmaceutical sales representative.

Doctor: {doctor_name}
Specialization: {specialization}
Recent Interaction Summary: {summary}
Sentiment: {sentiment}
Outcome: {outcome}
Previous Follow-up: {follow_up}
Interaction History: {history}

Provide actionable recommendations including:
1. Suggested timing for next meeting
2. Recommended materials or samples to bring
3. Key talking points based on previous concerns
4. Strategy based on the doctor's sentiment

Be specific, practical, and concise. Format as a clear list."""

EDIT_INTERACTION_PROMPT = """The user wants to edit an existing interaction. Analyze their request and determine what changes to make.

User message: {user_input}
Current interaction data: {current_interaction}

Identify the specific fields that need to be updated and their new values.
Respond with ONLY valid JSON containing only the fields that should be changed. Example:
{{
    "follow_up": "Friday, July 11",
    "sentiment": "positive"
}}"""
