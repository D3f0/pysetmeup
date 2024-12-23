from pyinfra.operations import apt, dnf, apk, server
from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName, Which


@deploy("Install git")
def deploy():
    if not host.get_fact(Which, command="git"):
        return

    if host.get_fact(LinuxName) == "RedHat":
        dnf.packages(
            name="Install git",
            packages=["git"],
            # update=True,
        )
    elif host.fact.os == "Darwin":
        server.shell(name="Install git via Homebrew", commands=["brew install git"])
    elif host.fact.os_family == "Alpine":
        apk.packages(name="Install git", packages=["git"])
    elif host.fact.os_family == "RedHat":
        dnf.packages(name="Install git", packages=["git"])
    elif host.fact.os_family == "Debian":
        apt.packages(name="Install git", packages=["git"])
