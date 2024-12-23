from pyinfra import host
from pyinfra.operations import server
from pyinfra.operations import dnf
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName, Which
from logging import getLogger

logger = getLogger(__name__)


@deploy("Install fzf")
def install():
    linux_name = host.get_fact(LinuxName)
    if not host.get_fact(Which, command="fzf"):
        return

    if linux_name in {"RedHat", "CentOS"}:
        dnf.packages(
            name="Install fzf",
            packages=["fzf"],
            # update=True,
        )
    elif linux_name == "Debian":
        server.apt.update()
        server.apt.packages(packages=["fzf"])
    else:
        raise LookupError(f"Can't find unzip for {linux_name}")
