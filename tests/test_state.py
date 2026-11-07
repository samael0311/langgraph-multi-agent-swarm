from app.state import EvidenceItem, CodeArtifact, AuditScore, ReportDeliverable, SwarmState


def test_evidence_item_schema():
    item = EvidenceItem(
        source_id="test_1",
        title="Test Source",
        url="https://test.internal",
        content_snippet="Snippet data",
        score=0.95
    )
    assert item.source_id == "test_1"
    assert item.score == 0.95


def test_code_artifact_schema():
    artifact = CodeArtifact(
        script_id="s1",
        code="print('hello')",
        stdout="hello\n",
        success=True
    )
    assert artifact.exit_code == 0
    assert artifact.success is True


def test_swarm_state_defaults():
    state = SwarmState(
        task_id="t1",
        user_query="Analyze multi-agent trends",
    )
    assert state.task_id == "t1"
    assert state.status == "initialized"
    assert state.current_step == 0
    assert state.revision_count == 0
    assert state.max_revisions == 2
    assert state.evidence == []
    assert state.code_artifacts == []
    assert state.final_report is None
