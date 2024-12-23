from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import Which, Command
from pyinfra.operations import server


@deploy(name="direnv environment manager")
def deploy(user: str = None):
    user = host.data.get("user", None)
    if not host.get_fact(Which, "direnv"):
        # Install
        server.shell("curl -sfL https://direnv.net/install.sh | bash", _su_user=user)

    if user:
        server.shell("direnv hook bash > $HOME/.bashrc.d/direnv.sh", _su_user=user)
        *_, default_shell = host.get_fact(
            Command, command="printenv SHELL", _su_user=user
        ).split("/")
        if default_shell == "fish":
            server.shell(
                "direnv hook fish > ~/.config/fish/conf.d/direnv.fish", _su_user=user
            )
        elif default_shell == "zsh":
            # TODO: Need to check for oh-my-zsh and enable this plugin
            raise LookupError("Not defined fos zsh")


if __name__ in {"builtins", "__main__"}:
    deploy()
