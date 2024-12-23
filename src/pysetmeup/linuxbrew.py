# pyinfra deploy.py <hostname>
from pyinfra.operations import server
from pyinfra.operations import dnf
from pyinfra.operations import systemd

from pyinfra import host
from pyinfra.facts.server import LinuxName, Path


server.shell(
    name="Set linuxbrew",
    commands=[
        """
        bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        """
    ],
    _su_user="nahuel",
)
