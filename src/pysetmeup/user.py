import getpass
from pyinfra.operations import server
from pyinfra.operations import git
from pyinfra.operations import files
from pyinfra import host
from pyinfra.facts.server import Command

from pyinfra.api import deploy
from pysetmeup.parts import bashrc_d_directory, fish, direnv


@deploy("setup a user")
def deploy():
    user = host.data.get("user", getpass.getuser())
    direnv.deploy()
    bashrc_d_directory.deploy(user=user)

    fish.deploy(_su_user=user)

    git.repo(
        name="tmux configuration from gpakosz",
        src="https://github.com/gpakosz/.tmux.git",
        dest=f"/home/{user}/.tmux",
        branch="master",
        user=user,
        _su_user=user,
    )

    files.link(
        name="Settings the ~/.tmux.conf to gpakosz",
        path=f"/home/{user}/.tmux.conf",
        target=f"/home/{user}/.tmux/.tmux.conf",
        user=user,
        force=True,
    )

    server.shell(
        name="Set the local overrides for tmux",
        commands="test -f ~/.tmux.conf.local || cp ~/.tmux/.tmux.conf.local ~/",
        _su_user=user,
    )

    # TODO: Should we do it only in interactive sessions like
    # in the ArchLinux wiki?
    shell = host.get_fact(Command, "which fish")
    server.user(
        name="Set the shell",
        user=user,
        shell=shell,
    )

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


if __name__ in {"builtins", "__main__"}:
    deploy()
