"""
To install docker check

https://github.com/pyinfra-dev/pyinfra-docker/blob/main/pyinfra_docker/docker.py
"""

# TODO: Verify this one

import io
from logging import getLogger
from textwrap import dedent
from pyinfra import host
from pyinfra.api.deploy import deploy
from pyinfra.api.exceptions import DeployError
from pyinfra.facts.server import Command, Which
from pyinfra.operations import files, server

logger = getLogger(__name__)


@deploy(name="Ensure docker is listening in TCP mode")
def ensure_docker_listening_tcp():
    if not host.get_fact(Which, "docker"):
        raise DeployError("Docker is not installed on the host")
    label_state = host.get_fact(Command, "systemctl show -p ActiveState docker")
    _, state = label_state.split("=")
    active = state == "active"
    logger.debug(active)

    if (
        host.get_fact(Command, "test -f /etc/docker/config.jsons && echo OK || echo NO")
        == "OK"
    ):
        raise DeployError("Update not implemented")

        # with tempfile.NamedTemporaryFile("w") as fp:
        #     config = files.get("/etc/docker/config.json", fp.name)
    else:
        src = io.StringIO(
            dedent(
                """\
                {
                    "hosts": ["unix:///var/run/docker.sock", "tcp://127.0.0.1:2375"]
                }
                """
            )
        )

        files.put(
            src,
            "/etc/docker/config.json",
        )
        server.shell("systemctl restart docker")


if __name__ in {"builtins", "__main__"}:
    ensure_docker_listening_tcp()
