from app.state import SwarmState, EvidenceItem, CodeArtifact
from app.agents.supervisor import SupervisorAgent
from app.agents.researcher import ResearcherAgent
from app.agents.coder import CoderAgent
from app.agents.critic import CriticAgent
from app.agents.synthesizer import SynthesizerAgent


def test_supervisor_planning():
    agent = SupervisorAgent()
    state = SwarmState(task_id="t_sup", user_query="LangGraph evaluation")
    res = agent.plan_and_route(state)
    assert res["status"] == "planned"
    assert len(res["plan"]) >= 4
    assert res["current_step"] == 1


def test_researcher_evidence_gathering():
    agent = ResearcherAgent()
    state = SwarmState(task_id="t_res", user_query="Enterprise agent architectures")
    res = agent.research(state)
    assert res["status"] == "research_completed"
    assert len(res["evidence"]) > 0
    assert any("ref_" in e.source_id for e in res["evidence"])


def test_coder_execution():
    agent = CoderAgent()
    state = SwarmState(
        task_id="t_code",
        user_query="Cost reduction modeling",
        evidence=[EvidenceItem(source_id="s1", title="Title", url="https://u", content_snippet="text", score=0.95)]
    )
    res = agent.analyze_and_compute(state)
    assert res["status"] == "analysis_completed"
    assert len(res["code_artifacts"]) == 1
    assert "EVIDENCE_COUNT:1" in res["code_artifacts"][0].stdout


def test_critic_passing_audit():
    agent = CriticAgent(pass_threshold=0.90)
    state = SwarmState(
        task_id="t_crit",
        user_query="Fact verification test",
        evidence=[EvidenceItem(source_id="s1", title="Source", url="https://u", content_snippet="text", score=0.98)],
        code_artifacts=[CodeArtifact(script_id="s1", code="print(1)", stdout="1", success=True)]
    )
    res = agent.audit(state)
    assert res["status"] == "audited_passed"
    assert res["audit"].passed is True
    assert res["audit"].groundedness_score >= 0.90


def test_critic_revision_loop_trigger():
    agent = CriticAgent(pass_threshold=0.95)
    # State with failed code artifact to simulate defect
    state = SwarmState(
        task_id="t_crit_fail",
        user_query="Fact verification failure test",
        evidence=[],  # No evidence -> low groundedness
        code_artifacts=[CodeArtifact(script_id="bad", code="assert False", stderr="AssertionError", exit_code=1, success=False)]
    )
    res = agent.audit(state)
    assert res["status"] == "audited_revision_required"
    assert res["audit"].passed is False


def test_synthesizer_output():
    agent = SynthesizerAgent()
    state = SwarmState(
        task_id="t_synth",
        user_query="Final deliverable test",
        evidence=[EvidenceItem(source_id="s1", title="Report Doc", url="https://doc.internal", content_snippet="snippet", score=0.98)],
        code_artifacts=[CodeArtifact(script_id="s1", code="print(1)", stdout="SPEEDUP:10x", success=True)],
        hitl_approved=True
    )
    res = agent.synthesize(state)
    assert res["status"] == "completed"
    assert res["final_report"] is not None
    assert "Executive Intelligence Dossier" in res["final_report"].title
    assert "SPEEDUP" in res["final_report"].markdown_content
