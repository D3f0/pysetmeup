from pyinfra import host
from pyinfra.operations import server
from pyinfra.operations import dnf
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName, Which
from logging import getLogger

logger = getLogger(__name__)


@deploy("Install unzip")
def install():
    """Install unzip"""
    if host.get_fact(Which, command="unzip"):
        return

    linux_name = host.get_fact(LinuxName)
    if linux_name in {"RedHat", "CentOS"}:
        if not host.get_fact(Which, command="unzip"):
            dnf.packages(
                name="Install unzip",
                packages=["unzip"],
                # update=True,
            )
    elif linux_name == "Alpine":
        server.apk.update(packages=["unzip"])
        server.apk.packages()
    elif linux_name == "Debian":
        server.apt.update()
        server.apt.packages(packages=["unzip"])
    else:
        raise LookupError(f"Can't find unzip for {linux_name}")
