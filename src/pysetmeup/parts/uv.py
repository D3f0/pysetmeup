from pyinfra.api import deploy
from pyinfra import host, logger
from pyinfra.operations import server
from pyinfra.facts import server as server_facts


@deploy("yq")
def deploy():
    if host.get_fact(server_facts.Which, "curl"):
        server.shell("curl -LsSf https://astral.sh/uv/install.sh | sh")
    else:
        logger.warning("Skipping uv install because curl is not available")
