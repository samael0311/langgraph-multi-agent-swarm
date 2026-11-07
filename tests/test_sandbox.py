import pytest
from app.sandbox.docker_repl import PythonSandboxRunner, SecurityViolationError


def test_sandbox_successful_execution():
    runner = PythonSandboxRunner(timeout_seconds=5, use_docker=False)
    code = "x = 40 + 2\nprint(f'RESULT:{x}')"
    artifact = runner.execute(code)
    assert artifact.success is True
    assert artifact.exit_code == 0
    assert "RESULT:42" in artifact.stdout


def test_sandbox_timeout_enforcement():
    runner = PythonSandboxRunner(timeout_seconds=1, use_docker=False)
    # Code that attempts to run indefinitely
    infinite_code = "import time\ntime.sleep(3)"
    artifact = runner.execute(infinite_code)
    assert artifact.success is False
    assert artifact.exit_code == 124
    assert "TimeoutExpired" in artifact.stderr


def test_sandbox_security_ast_blocking():
    runner = PythonSandboxRunner(timeout_seconds=5, use_docker=False)
    # Attempting blocked ctypes import
    malicious_code = "import ctypes\nprint('pwned')"
    artifact = runner.execute(malicious_code)
    assert artifact.success is False
    assert artifact.exit_code == 126
    assert "SecurityViolation" in artifact.stderr
