from pyinfra import host
from pyinfra.operations import server
from pyinfra.api import deploy
from pyinfra.facts.server import Which, Command, User
from logging import getLogger
from . import unzip

logger = getLogger(__name__)


@deploy("Install rclone")
def install():
    """Install rclone"""
    if host.get_fact(Which, command="rclone"):
        return
    unzip.install()
    user = host.get_fact(User)
    id = host.get_fact(Command, "id -u")

    if user == "root" or id == "0":
        prefix = ""
    else:
        prefix = "sudo"
    server.shell(f"curl https://rclone.org/install.sh | {prefix} bash")
