import getpass
from textwrap import dedent
from pyinfra.operations import server
from pyinfra.operations import git
from pyinfra.operations import files
from pyinfra import host
from pyinfra.facts.server import LinuxName, Which

from pyinfra.api import deploy
from pysetmeup.parts import bashrc_d_directory
from pysetmeup.parts import git


@deploy("setup a user")
def deploy():
    user = host.data.get("user", getpass.getuser())

    bashrc_d_directory.deploy()
    git.deploy()

    
    if host.get_fact(LinuxName) == "RedHat":
        
        if not host.get_fact(Which, command="fish"):
            # Fish from RedHat is a bit old
            # see https://packages.fedoraproject.org/pkgs/fish/fish/
            # dnf.packages(
            #     name="Install Friendly Interactive Shell 🐟",
            #     packages=["fish"],
            #     # update=True,
            # )
            ...
        else:
            server.shell(
                name="Install Recent version of fish 🐟 using WebInstaller for user",
                commands=["curl -sS https://webi.sh/fish | sh"],
                _su_user="nahuel",
            )
            # # Modify bashrc to drop into Fish
            # file.block(
            #     ...
            # )
        # if not host.get_fact(Which, "mosh"):

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

    server.user(
        name="Set the shell",
        user=user,
        shell="/usr/bin/fish",
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
