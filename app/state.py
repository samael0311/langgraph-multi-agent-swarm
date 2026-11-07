from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Represents a piece of verified external web or document evidence."""
    source_id: str
    title: str
    url: str
    content_snippet: str
    score: float = 1.0


class CodeArtifact(BaseModel):
    """Represents an isolated Python execution run and its outcome."""
    script_id: str
    code: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time_ms: float = 0.0
    success: bool = True


class AuditScore(BaseModel):
    """Result of the Critic agent evaluating groundedness and factual integrity."""
    groundedness_score: float = 1.0
    verified_claims: List[str] = Field(default_factory=list)
    hallucinated_claims: List[str] = Field(default_factory=list)
    missing_citations: List[str] = Field(default_factory=list)
    passed: bool = True
    feedback: str = ""


class ReportDeliverable(BaseModel):
    """Final synthesized client report with grounded citations and audit metadata."""
    title: str
    executive_summary: str
    key_findings: List[str] = Field(default_factory=list)
    quantitative_data: List[Dict[str, Any]] = Field(default_factory=list)
    citations: List[Dict[str, str]] = Field(default_factory=list)
    audit_trail: Dict[str, Any] = Field(default_factory=dict)
    markdown_content: str = ""


class SwarmState(BaseModel):
    """
    Central LangGraph state dictionary schema tracking dynamic multi-agent execution.
    """
    task_id: str
    user_query: str
    constraints: List[str] = Field(default_factory=list)
    plan: List[str] = Field(default_factory=list)
    current_step: int = 0
    
    # Tool and analysis outputs
    evidence: List[EvidenceItem] = Field(default_factory=list)
    code_artifacts: List[CodeArtifact] = Field(default_factory=list)
    draft_report: Optional[str] = None
    
    # Audit & Governance checkpoints
    audit: Optional[AuditScore] = None
    hitl_approved: bool = False
    revision_count: int = 0
    max_revisions: int = 2
    
    # Operational Lifecycle
    status: str = "initialized"
    final_report: Optional[ReportDeliverable] = None
    errors: List[str] = Field(default_factory=list)
