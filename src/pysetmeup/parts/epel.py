# https://docs.fedoraproject.org/en-US/epel/getting-started/
# dnf config-manager --set-enabled crb && dnf install https://dl.fedoraproject.org/pub/epel/epel{,-next}-release-latest-9.noarch.rpm
from pyinfra.operations import server
from pyinfra.operations import dnf
from pyinfra.api import deploy


@deploy("Install EPEL")
def install_epel_repositories():
    server.shell(
        name="Set up EPEL 1/3",
        commands=["dnf config-manager --set-enabled crb || true"],
    )

    dnf.rpm(
        name="Setup EPEL 2/3",
        src="https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm",
    )
    dnf.rpm(
        name="Setup EPEL 2/3",
        src="https://dl.fedoraproject.org/pub/epel/epel-next-release-latest-9.noarch.rpm",
    )
