import getpass

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files


@deploy()
def deploy(user: str = None):
    user = host.data.get("user", getpass.getuser())
    files.block(
        name="Add sudo config file",
        path=f"/etc/sudoers.d/sudo_{user}",
        content=f"{user} ALL=(ALL) NOPASSWD: ALL",
    )
