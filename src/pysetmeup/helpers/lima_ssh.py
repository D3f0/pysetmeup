"""
Ensures that all the lima VMs are in SSH
"""

import yaml

from pyinfra.operations import apt, python, server
from pyinfra.local import shell


def lima_machines(state, host):
    """
    Ensures that lima machines are available for SSH
    """
    out = shell(commands=["limactl ls --json | yq -pj '.name' -o t"], splitlines=True)
    breakpoint()


python.call(name="Find lima machines", function=lima_machines)
