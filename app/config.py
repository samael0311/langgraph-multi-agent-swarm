import os
from typing import Optional
from pydantic import BaseModel, Field


class SwarmSettings(BaseModel):
    """Configuration settings for the Multi-Agent Swarm system."""
    
    app_name: str = "LangGraph-Multi-Agent-Swarm"
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    
    # LLM & Model Parameters
    model_name: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))
    temperature: float = Field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.2")))
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    
    # Tool & Search Configuration
    tavily_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("TAVILY_API_KEY"))
    max_search_results: int = Field(default_factory=lambda: int(os.getenv("MAX_SEARCH_RESULTS", "5")))
    
    # Code Execution Sandbox Parameters
    sandbox_timeout_seconds: int = Field(default_factory=lambda: int(os.getenv("SANDBOX_TIMEOUT_SEC", "10")))
    sandbox_max_memory_mb: int = Field(default_factory=lambda: int(os.getenv("SANDBOX_MAX_MEMORY_MB", "512")))
    use_docker_sandbox: bool = Field(default_factory=lambda: os.getenv("USE_DOCKER_SANDBOX", "false").lower() == "true")
    
    # Swarm Execution Limits & Policies
    max_revisions: int = Field(default_factory=lambda: int(os.getenv("MAX_REVISIONS", "2")))
    critic_pass_threshold: float = Field(default_factory=lambda: float(os.getenv("CRITIC_PASS_THRESHOLD", "0.95")))
    hitl_auto_approve_threshold: float = Field(default_factory=lambda: float(os.getenv("HITL_AUTO_APPROVE_THRESHOLD", "0.98")))
    require_hitl_approval: bool = Field(default_factory=lambda: os.getenv("REQUIRE_HITL_APPROVAL", "true").lower() == "true")
    
    # State Persistence
    checkpoint_db_path: str = Field(default_factory=lambda: os.getenv("CHECKPOINT_DB_PATH", ":memory:"))


settings = SwarmSettings()
