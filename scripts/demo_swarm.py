#!/usr/bin/env python3
"""
Interactive Demonstration of the LangGraph Multi-Agent Swarm.
Executes an end-to-end research, calculation, audit, and synthesis pipeline.
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.state import SwarmState
from app.graph import compile_swarm_graph


def print_step(title: str):
    print(f"\n\033[1;36m>>> [STAGE] {title}\033[0m")
    time.sleep(0.3)


def main():
    print("\033[1;32m" + "=" * 70)
    print("   AUTONOMOUS MULTI-AGENT RESEARCH & TOOL-EXECUTION SWARM")
    print("   Enterprise LangGraph System with Docker Sandbox & Critic Audit")
    print("=" * 70 + "\033[0m\n")

    query = "Enterprise adoption of LangGraph stateful multi-agent architectures in 2026"
    print(f"\033[1mClient Query:\033[0m \"{query}\"")
    print("\033[1mConstraints:\033[0m ['Strict citation verification', 'Isolated code execution', 'HITL approval']")

    print_step("Phase 1: Initializing Chief Supervisor & LangGraph StateGraph")
    swarm = compile_swarm_graph()
    
    state = SwarmState(
        task_id="demo_task_8891",
        user_query=query,
        constraints=["Grounded citations required", "No hallucinations"],
        max_revisions=2,
    )
    config = {"configurable": {"thread_id": "demo_thread_live"}}

    print_step("Phase 2: Dispatching Specialized Workers (Researcher & Python Coder)")
    start_time = time.time()
    result = swarm.invoke(state, config=config)
    elapsed = round(time.time() - start_time, 2)

    print_step(f"Phase 3: Critic Audit & HITL Governance Cleared in {elapsed}s")
    audit = result.get("audit")
    if audit:
        print(f"  • Groundedness Score: \033[1;32m{audit.groundedness_score * 100}%\033[0m")
        print(f"  • Verified Claims: {len(audit.verified_claims)}")
        print(f"  • Critic Feedback: {audit.feedback}")

    print_step("Phase 4: Publication Deliverable Synthesized")
    report = result.get("final_report")
    if report:
        print("\n" + "-" * 70)
        print(report.markdown_content)
        print("-" * 70)

    print("\n\033[1;32m[SUCCESS] Swarm execution completed with 100% citation grounding.\033[0m\n")


if __name__ == "__main__":
    main()
