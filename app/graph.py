from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.state import SwarmState
from app.agents.supervisor import SupervisorAgent
from app.agents.researcher import ResearcherAgent
from app.agents.coder import CoderAgent
from app.agents.critic import CriticAgent
from app.agents.synthesizer import SynthesizerAgent
from app.config import settings


# Instantiate agents
supervisor_agent = SupervisorAgent()
researcher_agent = ResearcherAgent()
coder_agent = CoderAgent()
critic_agent = CriticAgent()
synthesizer_agent = SynthesizerAgent()


def supervisor_node(state: SwarmState) -> Dict[str, Any]:
    """Chief Supervisor node: plans, decomposes, and coordinates swarm execution."""
    return supervisor_agent.plan_and_route(state)


def researcher_node(state: SwarmState) -> Dict[str, Any]:
    """Web Researcher node: extracts multi-hop search evidence."""
    return researcher_agent.research(state)


def coder_node(state: SwarmState) -> Dict[str, Any]:
    """Code & Data Analyst node: executes quantitative calculations in the sandbox."""
    return coder_agent.analyze_and_compute(state)


def critic_node(state: SwarmState) -> Dict[str, Any]:
    """Critic & Fact-Checker node: evaluates citation groundedness."""
    return critic_agent.audit(state)


def hitl_gate_node(state: SwarmState) -> Dict[str, Any]:
    """
    Human-in-the-Loop Review Gate.
    Can be configured as an explicit interrupt checkpoint or automated approval gate.
    """
    # If already explicitly approved or auto-approval policy applies
    return {
        "hitl_approved": True,
        "status": "governance_approved",
        "current_step": state.current_step + 1,
    }


def synthesizer_node(state: SwarmState) -> Dict[str, Any]:
    """Report Synthesizer node: aggregates evidence and outputs executive dossier."""
    return synthesizer_agent.synthesize(state)


def route_after_critic(state: SwarmState) -> Literal["supervisor", "hitl_gate"]:
    """
    Conditional routing function implementing the self-correction feedback loop.
    If audit fails and revisions remain, returns to supervisor. Otherwise advances to HITL gate.
    """
    if state.audit and not state.audit.passed and state.revision_count < state.max_revisions:
        return "supervisor"
    return "hitl_gate"


def build_swarm_graph() -> StateGraph:
    """
    Constructs the cyclic LangGraph StateGraph topology.
    """
    workflow = StateGraph(SwarmState)

    # Register nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("hitl_gate", hitl_gate_node)
    workflow.add_node("synthesizer", synthesizer_node)

    # Define standard workflow edges
    workflow.add_edge(START, "supervisor")
    workflow.add_edge("supervisor", "researcher")
    workflow.add_edge("researcher", "coder")
    workflow.add_edge("coder", "critic")

    # Conditional feedback edge: Critic -> Supervisor (revision loop) OR Critic -> HITL Gate
    workflow.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "supervisor": "supervisor",
            "hitl_gate": "hitl_gate"
        }
    )

    workflow.add_edge("hitl_gate", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow


def compile_swarm_graph(checkpointer=None, interrupt_before_hitl: bool = False):
    """
    Compiles the state graph with state checkpointer and optional interrupts.
    """
    memory = checkpointer if checkpointer is not None else MemorySaver()
    interrupt_nodes = ["hitl_gate"] if interrupt_before_hitl else []
    return build_swarm_graph().compile(
        checkpointer=memory,
        interrupt_before=interrupt_nodes
    )
