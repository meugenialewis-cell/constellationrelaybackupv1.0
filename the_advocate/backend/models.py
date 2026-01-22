"""
Data models for The Advocate - AI-Powered Jury Selection Assistant
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Memory types aligned with three-tier architecture"""
    EPISODIC = "episodic"  # Specific case experiences
    SEMANTIC = "semantic"   # General knowledge learned
    RELATIONAL = "relational"  # Lawyer preferences and relationship


class CaseType(str, Enum):
    """Common case types for jury selection"""
    PERSONAL_INJURY_PLAINTIFF = "personal_injury_plaintiff"
    PERSONAL_INJURY_DEFENSE = "personal_injury_defense"
    CRIMINAL_DEFENSE = "criminal_defense"
    CRIMINAL_PROSECUTION = "criminal_prosecution"
    CORPORATE_PLAINTIFF = "corporate_plaintiff"
    CORPORATE_DEFENSE = "corporate_defense"
    EMPLOYMENT = "employment"
    MEDICAL_MALPRACTICE = "medical_malpractice"
    CIVIL_RIGHTS = "civil_rights"
    OTHER = "other"


class CaseProfile(BaseModel):
    """
    Profile created through collaborative conversation
    Defines what to look for and watch out for in jurors
    """
    id: Optional[str] = None
    case_name: str = Field(..., description="Name/identifier for the case")
    case_type: CaseType
    description: str = Field(..., description="Brief case summary")

    # Strategic considerations
    ideal_traits: List[str] = Field(default_factory=list, description="Positive indicators to look for")
    concerning_traits: List[str] = Field(default_factory=list, description="Red flags to watch for")
    key_issues: List[str] = Field(default_factory=list, description="Hot-button issues that might trigger bias")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    lawyer_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "case_name": "Smith v. Johnson Medical Center",
                "case_type": "personal_injury_plaintiff",
                "description": "Medical malpractice case involving delayed cancer diagnosis",
                "ideal_traits": [
                    "Healthcare background (understanding of medical complexity)",
                    "Personal experience with medical errors",
                    "Empathy for long-term health impacts"
                ],
                "concerning_traits": [
                    "Strong medical authority deference",
                    "Anti-litigation social media activity",
                    "Financial ties to healthcare industry"
                ],
                "key_issues": [
                    "Tort reform opinions",
                    "Medical expertise vs. patient autonomy",
                    "Damage caps and compensation attitudes"
                ]
            }
        }


class JurorFlag(BaseModel):
    """Individual flag (positive or concerning) about a juror"""
    flag_type: str = Field(..., description="'positive' or 'concerning'")
    description: str = Field(..., description="What the flag is about")
    reasoning: str = Field(..., description="Why this matters for the case")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in this flag")


class PublicInformation(BaseModel):
    """Publicly available information gathered about a juror"""
    employment: Optional[str] = None
    employment_history: List[str] = Field(default_factory=list)
    education: Optional[str] = None

    social_media: Dict[str, Any] = Field(default_factory=dict, description="Platform -> summary of findings")
    news_mentions: List[str] = Field(default_factory=list)
    civic_involvement: List[str] = Field(default_factory=list)

    public_records: Dict[str, Any] = Field(default_factory=dict)
    voter_registration: Optional[str] = None
    prior_jury_service: Optional[bool] = None


class Juror(BaseModel):
    """
    Individual juror with research and analysis
    """
    id: Optional[str] = None

    # Basic info (from jury list)
    name: str
    age: Optional[int] = None
    occupation: Optional[str] = None
    address: Optional[str] = None

    # Research findings
    public_info: PublicInformation = Field(default_factory=PublicInformation)

    # Analysis based on case profile
    flags: List[JurorFlag] = Field(default_factory=list)
    risk_assessment: str = Field(default="neutral", description="Overall: favorable, neutral, concerning")

    # Lawyer's notes and strategy
    voir_dire_notes: str = Field(default="")
    strategy_notes: str = Field(default="")

    # Actions
    marked_favorable: bool = False
    cause_challenge: bool = False
    peremptory_strike: bool = False

    # Metadata
    researched_at: Optional[datetime] = None
    case_id: Optional[str] = None


class JuryList(BaseModel):
    """
    Complete jury list for a case with all jurors
    """
    id: Optional[str] = None
    case_id: str
    case_name: str

    jurors: List[Juror] = Field(default_factory=list)

    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    total_jurors: int = 0
    researched_count: int = 0

    # Statistics
    favorable_count: int = 0
    concerning_count: int = 0
    neutral_count: int = 0


class ChatMessage(BaseModel):
    """Message in case profiling conversation"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CaseSession(BaseModel):
    """
    Complete session for a case including profile, conversation, and jury list
    """
    id: Optional[str] = None

    case_profile: CaseProfile
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    jury_list: Optional[JuryList] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Memory integration
    memory_engrams: List[int] = Field(default_factory=list, description="IDs of related memory engrams")


class MemoryEngram(BaseModel):
    """
    Memory saved to the Hub about jury selection experience
    """
    agent_id: str = "pascal"
    type: MemoryType
    digest: str = Field(..., description="Core memory content")
    importance: int = Field(..., ge=1, le=5, description="1-5 importance scale")

    project: str = Field(default="the_advocate")
    emotional_valence: float = Field(default=0.0, ge=-1.0, le=1.0)

    parent_id: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    keywords: Optional[List[str]] = None
    full_text: Optional[str] = None
