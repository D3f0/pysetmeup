import getpass

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files, server


@deploy()
def deploy(user: str = None):
    user = host.data.get("user", getpass.getuser())
    files.block(
        name="Add sudo config file",
        path=f"/etc/sudoers.d/sudo_{user}",
        content=f"{user} ALL=(ALL) NOPASSWD: ALL",
    )
    server.shell(
        name="Set sudoers file permissions",
        commands=f"chmod 0440 /etc/sudoers.d/sudo_{user}",
        # sudo=True
    )
