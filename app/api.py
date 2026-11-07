import uuid
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.state import SwarmState, ReportDeliverable
from app.graph import compile_swarm_graph
from app.config import settings

app = FastAPI(
    title="Autonomous Multi-Agent Research & Execution Swarm API",
    description="Enterprise LangGraph swarm microservice with Docker REPL sandbox, fact-checking critic, and HITL governance.",
    version="1.0.0"
)

# Persistent graph runtime with MemorySaver checkpointer
swarm_runtime = compile_swarm_graph()


class ExecuteRequest(BaseModel):
    user_query: str = Field(..., json_schema_extra={"example": "Benchmark LangGraph vs Autogen multi-agent latency"})
    constraints: List[str] = Field(default_factory=list, json_schema_extra={"example": ["Verify all citations", "Include quantitative speedup"]})
    max_revisions: int = Field(default=2, ge=0, le=5)
    thread_id: Optional[str] = None


class ExecuteResponse(BaseModel):
    task_id: str
    thread_id: str
    status: str
    revision_count: int
    hitl_approved: bool
    final_report: Optional[ReportDeliverable] = None
    errors: List[str] = Field(default_factory=list)


@app.get("/health", tags=["System"])
def health_check():
    """Returns microservice health and operational configuration."""
    return {
        "status": "online",
        "service": settings.app_name,
        "environment": settings.environment,
        "sandbox_docker_enabled": settings.use_docker_sandbox,
        "critic_threshold": settings.critic_pass_threshold,
    }


@app.post("/swarm/execute", response_model=ExecuteResponse, tags=["Swarm Execution"])
def execute_swarm(req: ExecuteRequest):
    """
    Executes an autonomous multi-agent swarm research cycle.
    Coordinates Chief Supervisor, Web Researcher, Python Sandbox Analyst, Critic, and Synthesizer.
    """
    task_id = str(uuid.uuid4())
    thread_id = req.thread_id or f"thread_{task_id[:8]}"

    initial_state = SwarmState(
        task_id=task_id,
        user_query=req.user_query,
        constraints=req.constraints,
        max_revisions=req.max_revisions,
    )

    config = {"configurable": {"thread_id": thread_id}}

    try:
        final_state_dict = swarm_runtime.invoke(initial_state, config=config)
        return ExecuteResponse(
            task_id=final_state_dict["task_id"],
            thread_id=thread_id,
            status=final_state_dict["status"],
            revision_count=final_state_dict["revision_count"],
            hitl_approved=final_state_dict["hitl_approved"],
            final_report=final_state_dict.get("final_report"),
            errors=final_state_dict.get("errors", []),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Swarm execution failed: {str(exc)}")


@app.get("/swarm/state/{thread_id}", tags=["State & Replay"])
def get_thread_state(thread_id: str):
    """
    Retrieves the persisted StateGraph checkpoint snapshot for a specific thread_id.
    """
    config = {"configurable": {"thread_id": thread_id}}
    checkpoint = swarm_runtime.get_state(config)
    
    if not checkpoint or not checkpoint.values:
        raise HTTPException(status_code=404, detail=f"No active state found for thread_id '{thread_id}'.")

    return {
        "thread_id": thread_id,
        "next_nodes": checkpoint.next,
        "values": checkpoint.values,
    }
