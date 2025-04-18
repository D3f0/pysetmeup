from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import Which
from pyinfra.operations import server


@deploy(name="Install github CLI")
def deploy(user: str = None):
    gh_location = host.get_fact(Which, "gh")
    user = user or host.data.get("user")
    if not gh_location:
        server.shell(
            "curl -sS https://webi.sh/gh | sh",
            _su_user=user,
            name="Installing github CLI",
        )


if __name__ in {"builtins", "__main__"}:
    deploy()
