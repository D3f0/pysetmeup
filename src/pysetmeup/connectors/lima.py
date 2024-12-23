from io import IOBase
from pyinfra.connectors.base import BaseConnector

from pyinfra.api.exceptions import InventoryError
from pyinfra.api.command import StringCommand
from pyinfra.api.arguments import ConnectorArguments
import subprocess
import json
from typing import TYPE_CHECKING, Any, Unpack

if TYPE_CHECKING:
    from pyinfra.api.arguments import ConnectorArguments
    from pyinfra.api.command import StringCommand
    from pyinfra.api.host import Host
    from pyinfra.api.state import State


class LimaConnector(BaseConnector):
    """
    Connector for managing Lima VMs using pyinfra.
    """

    handles_execution = True

    def __init__(self, state: "State", host: "Host"):
        super().__init__(state, host)
        if "/" in host.name:
            *_, self.instance_name = host.name.split("/")
        else:
            *_, self.instance_name = host.name

        if not self.instance_name:
            raise InventoryError("No Lima instance name provided!")

    @staticmethod
    def make_names_data(name=None):
        if not name:
            raise InventoryError("No docker lima VM ID provided!")

        yield (
            f"@lima/{name}",
            {"lima_identifier": name},
            ["@lima"],
        )

    @property
    def connected(self) -> bool:
        """Check if the Lima VM is running."""
        try:
            result = subprocess.run(
                ["limactl", "list", "--json"], capture_output=True, text=True
            )
            if result.returncode != 0:
                return False

            instances = json.loads(result.stdout)
            for instance in instances:
                if instance["name"] == self.instance_name:
                    return instance["status"] == "Running"
            return False
        except Exception:
            return False

    def connect(self, *args, **kwargs) -> None:
        """Ensure the Lima VM is running."""
        if not self.connected:
            try:
                subprocess.run(["limactl", "start", self.instance_name], check=True)
            except subprocess.CalledProcessError as e:
                raise InventoryError(f"Failed to start Lima VM: {e}")

    def run_shell_command(
        self,
        command: StringCommand,
        stdin: str | None = None,
        timeout: int | None = None,
        get_pty: bool = False,
        *args,
        **kwargs,
    ) -> tuple:
        """Execute a shell command in the Lima VM."""

        try:
            cmd = ["lima", "-n", self.instance_name]

            if isinstance(command, StringCommand):
                cmd.extend(str(command).split())
            else:
                cmd.append(str(command))

            process = subprocess.run(
                cmd,
                input=stdin.encode() if stdin else None,
                capture_output=True,
                timeout=timeout,
            )

            return (
                process.returncode,
                process.stdout.decode(),
                process.stderr.decode(),
            )
        except subprocess.TimeoutExpired:
            return (1, "", "Command timed out")
        except Exception as e:
            return (1, "", f"Error executing command: {e}")

    def get_host(self) -> str:
        """Get the hostname of the Lima VM."""
        try:
            result = subprocess.run(
                ["limactl", "list", "--json"], capture_output=True, text=True
            )
            instances = json.loads(result.stdout)
            for instance in instances:
                if instance["name"] == self.instance_name:
                    return instance.get("address", "unknown")
            return "unknown"
        except Exception:
            return "unknown"

    @staticmethod
    def generate_data() -> dict[str, Any]:
        """Generate data about available Lima VMs."""
        try:
            result = subprocess.run(
                ["limactl", "list", "--json"], capture_output=True, text=True
            )
            return {"instances": json.loads(result.stdout)}
        except Exception:
            return {"instances": []}

    def get_file(
        self, remote_filename: str, local_filename: str, *args, **kwargs
    ) -> bool:
        """Copy a file from the Lima VM to the local machine."""
        try:
            subprocess.run(
                [
                    "lima",
                    "-n",
                    self.instance_name,
                    "cp",
                    f"{self.instance_name}:{remote_filename}",
                    local_filename,
                ],
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def put_file(
        self,
        filename_or_io: str | IOBase,
        remote_filename: str,
        *args,
        **arguments: Unpack["ConnectorArguments"],
    ) -> bool:
        """Copy a file from the local machine to the Lima VM."""
        try:
            subprocess.run(
                [
                    "lima",
                    "-n",
                    self.instance_name,
                    "cp",
                    filename_or_io,
                    f"{self.instance_name}:{remote_filename}",
                ],
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False
