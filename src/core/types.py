"""
Core Types Definition
By introducing TypedDict, we enforce type safety on dictionary structures used across the application.
"""
from typing import TypedDict, List, Optional, Union, Literal

class DiffLine(TypedDict):
    """Line-by-line diff result"""
    type: Literal["unchanged", "removed", "added"]
    content: str
    line: int

class ProcessingSuccess(TypedDict):
    """Successful processing result"""
    result: str
    seasoning: int
    model_used: Optional[str]
    from_cache: Optional[bool]

class ProcessingError(TypedDict):
    """Failed processing result"""
    error: str
    message: Optional[str]
    action: Optional[str]

# Union type for function return signatures
ProcessingResult = Union[ProcessingSuccess, ProcessingError]

class PrivacyRisk(TypedDict):
    """Result of privacy scan for a specific category"""
    risk_type: str
    count: int
    matches: List[str]

class ScanResult(TypedDict):
    """Overall privacy scan result"""
    has_risks: bool
    risks: dict[str, List[str]]
    risk_count: int
    message: Optional[str]

class SyncJobResult(TypedDict):
    """SyncJob status result"""
    job_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    result: Optional[str]
    created_at: str
