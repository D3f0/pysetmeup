from pyinfra import host, logger
from pyinfra.api import deploy
from pyinfra.facts.server import Which, Command, Kernel
from pyinfra.operations import server
from . import bashrc_d_directory


@deploy(name="direnv environment manager")
def deploy(user: str = None):
    user = host.data.get("user", None)
    if not user:
        user = host.get_fact(Command, "whoami")
    kernel = kernel = host.get_fact(Kernel)

    # Install
    if not host.get_fact(Which, "direnv"):
        if kernel == "Linux":
            # Install Linux
            server.shell(
                "curl -sfL https://direnv.net/install.sh | bash",
                _su_user=user,
                name="Installing direnv",
            )
        elif kernel == "Darwin":
            server.shell("brew install direnv")
    # Shell Hooking
    if kernel == "Linux":
        *_, default_shell = host.get_fact(
            Command, command="printenv SHELL", _su_user=user
        ).split("/")
        match default_shell:
            case "bash":
                bashrc_d_directory.deploy(name="Settings up bash's rc configs")
                if (
                    host.get_fact(
                        Command,
                        "test -f $HOME/.bashrc.d/99_direnv.sh || echo missing",
                    )
                    == "missing"
                ):
                    server.shell(
                        "direnv hook bash > $HOME/.bashrc.d/99_direnv.sh", _su_user=user
                    )
            case "fish":
                server.shell(
                    "direnv hook fish > ~/.config/fish/conf.d/direnv.fish",
                    _su_user=user,
                )
            case "zsh":
                # TODO: Need to check for oh-my-zsh and enable this plugin
                raise LookupError("Not defined fos zsh")
    elif kernel == "Darwin":
        logger.warning(
            "Shell hook on OSX not yet supported, please install it manually"
        )
    else:
        logger.warning("Shell hook in non Unix system not supported.")


if __name__ in {"builtins", "__main__"}:
    deploy()
