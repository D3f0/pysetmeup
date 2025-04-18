import getpass
from pyinfra.operations import server
from pyinfra.operations import files
from pyinfra import host, logger
from pyinfra.facts.server import Command

from pyinfra.api import deploy
from pysetmeup.parts import (
    bashrc_d_directory,
    fish,
    direnv,
    passwordless_sudo,
    tmux_config,
)


@deploy("setup a user")
def deploy():
    user = host.data.get("user", getpass.getuser())
    direnv.deploy(name="Setup direnv")
    bashrc_d_directory.deploy()

    # TODO: Should we do it only in interactive sessions like
    # in the ArchLinux wiki?
    try:
        fish.deploy(_su_user=user)
        shell = host.get_fact(Command, "which fish || echo missing")
        server.user(
            name="Set the shell",
            user=user,
            shell=shell,
        )
    except Exception:
        logger.error("Can't set the fish shell")

    tmux_config.deploy(user=user)

    files.directory(
        name="Local binaries",
        path=f"/home/{user}/.local/bin",
        user=user,
        _su_user=user,
    )

    files.block(
        name="Ensure ~/.local/bin is in the path",
        path=f"/home/{user}/.config/fish/config.fish",
        content=[f"fish_add_path /home/{user}/.local/bin"],
    )

    server.shell(
        name="Install starship 🚀",
        commands=[
            'which starship || sh -c "$(curl -fsSL https://starship.rs/install.sh)" -- --bin-dir $HOME/.local/bin/ --yes',
        ],
        _su_user=user,
    )

    files.block(
        name="Starship 🚀 shell initialization for fish 🐟",
        content="starship init fish | source",
        before=True,
        line="end",
        path=f"/home/{user}/.config/fish/config.fish",
        _su_user=user,
    )

    passwordless_sudo.deploy(user=user)


if __name__ in {"builtins", "__main__"}:
    deploy()
