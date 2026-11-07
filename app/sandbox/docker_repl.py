import sys
import time
import subprocess
import tempfile
import ast
from pathlib import Path
from typing import Optional
from app.state import CodeArtifact
from app.config import settings


class SecurityViolationError(Exception):
    """Raised when code violates AST security constraints."""
    pass


class PythonSandboxRunner:
    """
    Sandboxed Python REPL execution engine.
    Runs untrusted code with memory constraints, execution timeouts,
    and optional Docker container isolation.
    """

    def __init__(
        self,
        timeout_seconds: int = settings.sandbox_timeout_seconds,
        max_memory_mb: int = settings.sandbox_max_memory_mb,
        use_docker: bool = settings.use_docker_sandbox,
    ):
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb
        self.use_docker = use_docker

    def validate_safety(self, code_str: str) -> None:
        """
        Static AST audit to block overt malicious constructs
        when running in local fallback sandbox mode.
        """
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            raise SecurityViolationError(f"Code syntax error: {str(e)}")

        blocked_calls = {"exec", "eval", "__import__"}
        blocked_modules = {"pty", "ctypes", "winreg"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in blocked_modules:
                        raise SecurityViolationError(f"Import of blocked module '{root}' is prohibited.")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root = node.module.split(".")[0]
                    if root in blocked_modules:
                        raise SecurityViolationError(f"Import from blocked module '{root}' is prohibited.")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in blocked_calls:
                    raise SecurityViolationError(f"Dynamic invocation of '{node.func.id}()' is prohibited.")

    def execute(self, code_str: str, script_id: Optional[str] = None) -> CodeArtifact:
        """
        Executes the provided Python script within resource and time bounds.
        """
        s_id = script_id or f"script_{int(time.time() * 1000)}"
        start_time = time.perf_counter()

        # Step 1: Pre-execution static security audit
        try:
            self.validate_safety(code_str)
        except SecurityViolationError as sve:
            return CodeArtifact(
                script_id=s_id,
                code=code_str,
                stdout="",
                stderr=f"SecurityViolation: {str(sve)}",
                exit_code=126,
                execution_time_ms=0.0,
                success=False,
            )

        # Step 2: Write script to a temporary sandboxed execution file
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
            tmp.write(code_str)
            tmp_path = Path(tmp.name)

        try:
            if self.use_docker:
                # Docker containerized execution command with memory limits and zero network
                cmd = [
                    "docker", "run", "--rm",
                    "--network", "none",
                    "--memory", f"{self.max_memory_mb}m",
                    "-v", f"{tmp_path.parent}:/workspace:ro",
                    "python:3.10-slim",
                    "python", f"/workspace/{tmp_path.name}"
                ]
            else:
                # Local process isolation with strict timeout
                cmd = [sys.executable, str(tmp_path)]

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            return CodeArtifact(
                script_id=s_id,
                code=code_str,
                stdout=proc.stdout.strip(),
                stderr=proc.stderr.strip(),
                exit_code=proc.returncode,
                execution_time_ms=round(elapsed_ms, 2),
                success=(proc.returncode == 0),
            )

        except subprocess.TimeoutExpired:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return CodeArtifact(
                script_id=s_id,
                code=code_str,
                stdout="",
                stderr=f"TimeoutExpired: Execution exceeded safety limit of {self.timeout_seconds}s.",
                exit_code=124,
                execution_time_ms=round(elapsed_ms, 2),
                success=False,
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return CodeArtifact(
                script_id=s_id,
                code=code_str,
                stdout="",
                stderr=f"ExecutionError: {str(exc)}",
                exit_code=1,
                execution_time_ms=round(elapsed_ms, 2),
                success=False,
            )
        finally:
            # Clean up temporary execution artifact
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except OSError:
                pass
