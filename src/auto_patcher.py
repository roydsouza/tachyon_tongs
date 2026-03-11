import os
import subprocess
from src.state_manager import StateManager

class AutoPatcher:
    """
    The surgical limb of the Tachyon Tongs organism.
    Executes autonomous code mutation, triggers test regimens, and reverts upon failure (The 3-Attempt Loop).
    """

    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.state_manager = StateManager()

    def apply_and_test(self, patch_files: dict, test_file_path: str, test_content: str, cve_id: str):
        """
        Attempts to write new code, run a synthesized test, and handle the outcome.
        patch_files: Dict of { "src/file.py": "new_code_string" }
        """
        success = False
        revert_required = False

        # 1. Write the Regression Test
        try:
            with open(test_file_path, "w") as f:
                f.write(test_content)
        except Exception as e:
            return {"status": "error", "reason": f"Failed to write regression test: {e}"}

        # 2. Apply the Patches
        for file_path, new_content in patch_files.items():
            try:
                with open(file_path, "w") as f:
                    f.write(new_content)
            except Exception as e:
                return {"status": "error", "reason": f"Failed to apply patch to {file_path}: {e}"}

        # 3. Run the Regression Pipeline
        try:
            # We run pytest specifically on the synthesized test file
            result = subprocess.run(
                ["venv/bin/pytest", test_file_path, "-v"],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode == 0:
                success = True
                self.state_manager.log_evolution(
                    event_type="Successful Autonomous Mitigation",
                    details=f"Organism successfully synthesized an infrastructure patch for `{cve_id}`. Regression test `{test_file_path}` passed organically."
                )
                return {"status": "success", "message": result.stdout}
            else:
                revert_required = True
                traceback = result.stdout + "\n" + result.stderr
        except subprocess.TimeoutExpired:
            revert_required = True
            traceback = "Pytest execution timed out (possible infinite loop in synthesized patch)."
        except Exception as e:
            revert_required = True
            traceback = str(e)

        # 4. Handle Failure (The Revert)
        if revert_required:
            self._execute_revert(cve_id, traceback)
            return {"status": "failure", "traceback": traceback}

    def _execute_revert(self, cve_id: str, traceback: str):
        """Executes the Git Revert Safety Net to preserve the organism."""
        try:
            subprocess.run(["git", "checkout", "src/", "policies/", "tests/"], check=True)
            
            # Write Post-Mortem
            with open("ERROR.md", "w") as f:
                f.write(f"# 🚨 Autonomous Patching Failure\n\n**Target:** {cve_id}\n\nThe organism attempted to mutate its active defense, but the regression tests failed. The host has been reverted back to a stable cryptographic state.\n\n### Pytest Traceback\n```text\n{traceback}\n```\n")
            
            self.state_manager.log_evolution(
                event_type="Failed Autonomous Mitigation (Reverted)",
                details=f"Organism attempted infrastructure patch for `{cve_id}`. Regression tests failed. Codebase reverted. View `ERROR.md` for telemetry."
            )
        except Exception as e:
            # If git checkout fails, we are in deep trouble.
            self.state_manager.log_evolution(
                event_type="FATAL: Organism Corruption",
                details=f"Git revert failed during auto-healing loop for `{cve_id}`. Manual intervention required immediately. Error: {e}"
            )
