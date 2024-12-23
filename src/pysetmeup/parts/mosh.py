from pyinfra.api import deploy
from pyinfra import host
from pyinfra.operations import dnf, apt
from pyinfra.facts.server import LinuxName, Which


@deploy(name="Install mosh")
def deploy():
    if not host.get_fact(Which, command="mosh"):
        return

    if host.get_fact(LinuxName) == "RedHat":
        dnf.packages(
            name="Install mosh shell",
            packages=["mosh"],
        )
    elif host.get_fact(LinuxName) == "Debian":
        apt.packages(
            name="Install mosh shell",
            packages=["mosh"],
        )


if __name__ in ("__main__", "builtins"):
    deploy()
