"""
Recommendation Models.

Pydantic models for multi-criteria recommendation system.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class CriteriaField(BaseModel):
    """
    Individual criteria field configuration.

    Used within criteria_config JSON for each criterion.
    """
    weight: float = Field(ge=0.0, le=1.0, description="Weight/importance of this criterion (0-1)")
    values: Optional[List[str]] = Field(None, description="List of acceptable values (for categorical fields)")
    value: Optional[Any] = Field(None, description="Single acceptable value")
    min: Optional[float] = Field(None, description="Minimum value (for numeric fields)")
    max: Optional[float] = Field(None, description="Maximum value (for numeric fields)")


class CriteriaPresetCreate(BaseModel):
    """Create new criteria preset."""
    name: str = Field(..., min_length=1, max_length=200, description="Preset name")
    description: Optional[str] = Field(None, description="Preset description")
    criteria_config: Dict[str, Dict[str, Any]] = Field(..., description="Criteria configuration JSON")
    is_default: bool = Field(False, description="Whether this is a default preset")


class CriteriaPresetUpdate(BaseModel):
    """Update existing criteria preset."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    criteria_config: Optional[Dict[str, Dict[str, Any]]] = None
    is_default: Optional[bool] = None


class CriteriaPresetResponse(BaseModel):
    """Criteria preset response."""
    id: UUID
    name: str
    description: Optional[str]
    criteria_config: Dict[str, Dict[str, Any]]
    is_default: bool
    use_count: int
    created_at: datetime
    updated_at: datetime


class RecommendationRequest(BaseModel):
    """Request for media recommendations."""
    preset_id: Optional[UUID] = Field(None, description="Use existing preset by ID")
    criteria_config: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Custom criteria (if not using preset)"
    )
    limit: int = Field(10, ge=1, le=100, description="Maximum number of recommendations")
    exclude_watched: bool = Field(False, description="Exclude already watched media")
    min_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum score threshold")


class ScoredMedia(BaseModel):
    """Media item with recommendation score."""
    media: Dict[str, Any]  # Full media object
    score: float = Field(ge=0.0, le=1.0, description="Recommendation score (0-1)")
    score_breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="Score breakdown by criterion"
    )
    matched_criteria: List[str] = Field(
        default_factory=list,
        description="List of criteria that were matched"
    )


class RecommendationResponse(BaseModel):
    """Recommendation response with ranked results."""
    recommendations: List[ScoredMedia]
    total_candidates: int = Field(description="Total media items evaluated")
    criteria_used: Dict[str, Dict[str, Any]] = Field(description="Criteria configuration used")
    preset_name: Optional[str] = Field(None, description="Preset name if used")
    execution_time_ms: float = Field(description="Algorithm execution time")


class AvailableField(BaseModel):
    """Available field for criteria building."""
    field_name: str
    field_type: str  # 'string', 'number', 'boolean', 'array', 'date'
    display_name: str
    description: Optional[str]
    supports_min_max: bool = False
    supports_values: bool = False
    example_values: Optional[List[Any]] = None


class AvailableFieldsResponse(BaseModel):
    """Response with all available criteria fields."""
    fields: List[AvailableField]
    categories: Dict[str, List[str]] = Field(
        description="Fields grouped by category"
    )
