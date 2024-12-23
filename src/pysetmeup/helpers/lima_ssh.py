"""
Ensures that all the lima VMs are in SSH
"""

from pyinfra.operations import python
from pyinfra.local import shell


def lima_machines(state, host):
    """
    Ensures that lima machines are available for SSH
    """
    _out = shell(commands=["limactl ls --json | yq -pj '.name' -o t"], splitlines=True)


python.call(name="Find lima machines", function=lima_machines)
