"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
import datetime as dt
from enum import Enum


# ─── Enums ───────────────────────────────────────────────────────────

class SentimentEnum(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class InteractionTypeEnum(str, Enum):
    IN_PERSON = "in_person"
    VIRTUAL = "virtual"
    PHONE = "phone"
    EMAIL = "email"
    CONFERENCE = "conference"


# ─── HCP Schemas ─────────────────────────────────────────────────────

class HCPBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    specialization: Optional[str] = None
    hospital: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class HCPCreate(HCPBase):
    pass


class HCPResponse(HCPBase):
    id: int

    class Config:
        from_attributes = True


# ─── Material Schemas ────────────────────────────────────────────────

class MaterialBase(BaseModel):
    medicine_name: str = Field(..., min_length=1, max_length=200)
    quantity: int = Field(default=0, ge=0)


class MaterialCreate(MaterialBase):
    pass


class MaterialResponse(MaterialBase):
    id: int
    interaction_id: int

    class Config:
        from_attributes = True


# ─── Sample Distribution Schemas ─────────────────────────────────────

class SampleBase(BaseModel):
    sample_name: str = Field(..., min_length=1, max_length=200)
    count: int = Field(default=0, ge=0)


class SampleCreate(SampleBase):
    pass


class SampleResponse(SampleBase):
    id: int
    interaction_id: int

    class Config:
        from_attributes = True


# ─── Interaction Schemas ─────────────────────────────────────────────

class InteractionBase(BaseModel):
    hcp_id: int
    date: dt.date = Field(default_factory=dt.date.today)
    interaction_type: InteractionTypeEnum = InteractionTypeEnum.IN_PERSON
    topics: Optional[str] = None
    summary: Optional[str] = None
    sentiment: SentimentEnum = SentimentEnum.NEUTRAL
    outcome: Optional[str] = None
    follow_up: Optional[str] = None


class InteractionCreate(InteractionBase):
    materials: Optional[List[MaterialCreate]] = []
    samples: Optional[List[SampleCreate]] = []


class InteractionUpdate(BaseModel):
    hcp_id: Optional[int] = None
    date: Optional[dt.date] = None
    interaction_type: Optional[InteractionTypeEnum] = None
    topics: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[SentimentEnum] = None
    outcome: Optional[str] = None
    follow_up: Optional[str] = None
    materials: Optional[List[MaterialCreate]] = None
    samples: Optional[List[SampleCreate]] = None


class InteractionResponse(InteractionBase):
    id: int
    created_at: dt.datetime
    updated_at: dt.datetime
    hcp: Optional[HCPResponse] = None
    materials: List[MaterialResponse] = []
    samples: List[SampleResponse] = []

    class Config:
        from_attributes = True


class InteractionListResponse(BaseModel):
    interactions: List[InteractionResponse]
    total: int


# ─── Chat / Agent Schemas ────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_history: Optional[List[ChatMessage]] = []
    session_id: Optional[str] = None
    current_doctor: Optional[str] = None


class ExtractedEntities(BaseModel):
    doctor_name: Optional[str] = None
    doctor_id: Optional[int] = None
    products: Optional[List[str]] = []
    sentiment: Optional[SentimentEnum] = None
    summary: Optional[str] = None
    outcome: Optional[str] = None
    follow_up: Optional[str] = None
    samples: Optional[List[SampleCreate]] = []
    materials: Optional[List[MaterialCreate]] = []
    topics: Optional[str] = None
    interaction_type: Optional[InteractionTypeEnum] = None
    date: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    extracted_entities: Optional[ExtractedEntities] = None
    tool_used: Optional[str] = None
    interaction_id: Optional[int] = None
    data: Optional[dict] = None
