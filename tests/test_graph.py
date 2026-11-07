from app.state import SwarmState
from app.graph import compile_swarm_graph


def test_full_graph_execution():
    swarm = compile_swarm_graph()
    state = SwarmState(
        task_id="graph_test_1",
        user_query="LangGraph multi-agent orchestration benchmarks",
        constraints=["Zero hallucinations", "Deterministic math verification"],
    )
    config = {"configurable": {"thread_id": "thread_graph_test"}}

    final_state = swarm.invoke(state, config=config)

    assert final_state["status"] == "completed"
    assert final_state["hitl_approved"] is True
    assert final_state["final_report"] is not None
    assert len(final_state["evidence"]) > 0
    assert len(final_state["code_artifacts"]) > 0


def test_graph_checkpointer_persistence():
    swarm = compile_swarm_graph()
    thread_id = "thread_persistence_test"
    config = {"configurable": {"thread_id": thread_id}}

    state = SwarmState(
        task_id="persist_task_1",
        user_query="Market intelligence analysis",
    )
    swarm.invoke(state, config=config)

    # Fetch persisted state from memory checkpointer
    saved_state = swarm.get_state(config)
    assert saved_state is not None
    assert saved_state.values["task_id"] == "persist_task_1"
    assert saved_state.values["status"] == "completed"
