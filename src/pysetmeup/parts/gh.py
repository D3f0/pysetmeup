from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import Which
from pyinfra.operations import server


@deploy(name="Install github CLI")
def deploy():
    gh_location = host.get_fact(Which, "gh")
    if not gh_location:
        server.shell("curl -sS https://webi.sh/gh | sh")


if __name__ in {"builtins", "__main__"}:
    deploy()
