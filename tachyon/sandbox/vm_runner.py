import subprocess
import os
import yaml
import logging
from typing import Optional

logger = logging.getLogger("tachyon.sandbox.vm")

class VmRunner:
    """
    Tier 0 Hardware-Level Isolation using Lima (Virtualization.framework).
    Runs high-privilege agents in a dedicated MicroVM.
    """
    
    def __init__(self, instance_name: str = "tachyon-agent"):
        self.instance_name = instance_name
        self.template_path = "tachyon/sandbox/templates/agent-minimal.yaml"

    def provision_vm(self):
        """
        Initializes the Lima VM instance if it doesn't exist.
        """
        logger.info(f"Provisioning MicroVM: {self.instance_name}")
        try:
            cmd = ["limactl", "start", "--name", self.instance_name, self.template_path, "--tty=false"]
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to provision VM: {e}")
            raise

    def execute_command(self, command: str) -> str:
        """
        Executes a command inside the isolated MicroVM.
        """
        logger.info(f"Executing command in VM: {command}")
        try:
            cmd = ["limactl", "shell", self.instance_name, "bash", "-c", command]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"VM command execution failed: {e.stderr}")
            return f"ERROR: {e.stderr}"

    def stop_vm(self):
        """
        Shuts down the MicroVM instance.
        """
        logger.info(f"Shutting down MicroVM: {self.instance_name}")
        subprocess.run(["limactl", "stop", self.instance_name])
