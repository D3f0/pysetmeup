from pyinfra.api import deploy
from pyinfra import host, logger
from pyinfra.operations import server
from pyinfra.facts import server as server_facts


@deploy("uv")
def deploy(user: str | None = ""):
    user = user or host.data.get(
        "user",
    )
    if host.get_fact(server_facts.Which, "curl"):
        server.shell("curl -LsSf https://astral.sh/uv/install.sh | sh", _su_user=user)
    else:
        logger.warning("Skipping uv install because curl is not available")
