from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class IssueType(str, Enum):
    MISSING_VALUES = "missing_values"
    DUPLICATES = "duplicates"
    FORMAT_ERRORS = "format_errors"
    OUTLIERS = "outliers"
    INCONSISTENCIES = "inconsistencies"
    DATA_TYPE_MISMATCH = "data_type_mismatch"


class FixType(str, Enum):
    FILL_MISSING = "fill_missing"
    REMOVE_DUPLICATES = "remove_duplicates"
    STANDARDIZE_FORMAT = "standardize_format"
    CORRECT_OUTLIER = "correct_outlier"
    CONVERT_TYPE = "convert_type"
    STANDARDIZE_CASE = "standardize_case"


class DataUpload(BaseModel):
    upload_id: str
    filename: str
    file_size: int
    upload_time: datetime
    file_path: str
    status: str = "uploaded"


class DataIssue(BaseModel):
    issue_type: IssueType
    column: str
    description: str
    affected_rows: List[int]
    severity: str  # "low", "medium", "high", "critical"
    suggested_fix: Optional[str] = None
    confidence: float = Field(ge=0, le=1)  # Confidence in the issue detection


class DataFix(BaseModel):
    fix_type: FixType
    column: str
    description: str
    rows_affected: List[int]
    old_values: List[Any]
    new_values: List[Any]
    confidence: float = Field(ge=0, le=1)
    uncertainty_reason: Optional[str] = None


class DataQualityReport(BaseModel):
    upload_id: str
    quality_score: float = Field(ge=0, le=1)
    total_rows: int
    total_columns: int
    issues: List[DataIssue]
    recommendations: List[str]
    analysis_timestamp: datetime = Field(default_factory=datetime.now)


class ConversationMessage(BaseModel):
    content: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class AnomalyDetection(BaseModel):
    column: str
    anomaly_type: str
    affected_rows: List[int]
    statistical_measure: str
    threshold_value: float
    actual_values: List[Any]
    suggested_correction: Optional[Any] = None


class DataLineage(BaseModel):
    upload_id: str
    transformations: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.now)


class RootCauseAnalysis(BaseModel):
    issue_id: str
    potential_causes: List[str]
    source_system: Optional[str] = None
    ingestion_step: Optional[str] = None
    transformation_step: Optional[str] = None
    confidence_score: float = Field(ge=0, le=1)
