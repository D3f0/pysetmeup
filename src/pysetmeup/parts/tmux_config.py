from textwrap import dedent
from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import git, server
from pyinfra.facts.server import Home


@deploy("Set tmux config")
def deploy(user: str | None = ""):
    """
    Sets the tmux configuration form https://github.com/gpakosz/.tmux
    """
    user = user or host.data.get(
        "user",
    )
    home = host.get_fact(Home, user=user)
    dest = f"{home}/.tmux"
    git.repo(
        name="tmux configuration from gpakosz",
        src="https://github.com/gpakosz/.tmux.git",
        dest=dest,
        branch="master",
        user=user,
        _su_user=user,
    )
    server.shell(
        dedent(f"""
        if [ ! -f {home}/.tmux.conf ]; then
            ln -sf {dest}/.tmux.conf  {home}/
        fi
        """),
        name=f"Setting .tmux.conf in {home} if not present...",
        _su_user=user,
    )
    # server.shell(
    #     name="Set the local overrides for tmux",
    #     commands="test -f ~/.tmux.conf.local || cp ~/.tmux/.tmux.conf.local ~/",
    #     _su_user=user,
    # )
    server.shell(
        dedent(f"""
        if [ ! -f {home}/.tmux.conf.local ]; then
            cp {dest}/.tmux.conf.local  {home}/
        fi
        """),
        name=f"Setting .tmux.conf.local in {home} if not present...",
        _su_user=user,
    )
