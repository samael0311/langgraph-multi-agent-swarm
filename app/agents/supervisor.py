from typing import Dict, Any
from app.state import SwarmState


class SupervisorAgent:
    """
    Chief Supervisor orchestrator managing the StateGraph workflow.
    Decomposes client queries into sequential execution stages,
    dispatches work to worker agents, and handles self-correction loops.
    """

    def __init__(self, name: str = "ChiefSupervisor"):
        self.name = name

    def plan_and_route(self, state: SwarmState) -> Dict[str, Any]:
        """
        Evaluates current graph state and updates the plan or routing instructions.
        """
        # If this is a revision loop triggered by the Critic
        if state.audit and not state.audit.passed and state.revision_count < state.max_revisions:
            new_rev_count = state.revision_count + 1
            revised_plan = [
                f"Address Critic Feedback: {state.audit.feedback}",
                "Re-query supplemental evidence for flagged missing citations",
                "Re-compute statistical calculations in Python sandbox",
                "Re-submit to Critic for final verification"
            ]
            return {
                "plan": revised_plan,
                "revision_count": new_rev_count,
                "status": f"revising_turn_{new_rev_count}",
                "current_step": 1,
            }

        # Initial plan decomposition
        if not state.plan:
            initial_plan = [
                f"1. Perform multi-source web evidence extraction for query: '{state.user_query}'",
                "2. Execute deterministic Python computations for quantitative metrics in isolated sandbox",
                "3. Perform citation audit & groundedness evaluation via Critic Agent",
                "4. Await Human-in-the-Loop review & safety checkpoint approval",
                "5. Synthesize publication-ready executive report with audit metadata"
            ]
            return {
                "plan": initial_plan,
                "current_step": 1,
                "status": "planned",
            }

        return {
            "current_step": state.current_step + 1,
            "status": "in_progress",
        }
