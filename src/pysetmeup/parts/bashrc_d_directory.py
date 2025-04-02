"""
Creates a ~/.bashrc.d/ directory and ensures that the ~/.basrc.d
loads the scripts that are placed in there.
"""

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files
from pyinfra.facts.server import Home, Command
from textwrap import dedent


@deploy(name="Create ~/.bashrc.d directory")
def deploy():
    user = host.data.get("user", host.get_fact(Command, "whoami"))
    home = host.get_fact(Home, user=user)
    mounted_mac = host.get_fact(Command, "test -d /Users/ && echo OK || echo NO")

    # In lima vms the su command can't be used
    kw_args = {}
    if mounted_mac and home.endswith(".linux"):
        kw_args["sudo"] = True

    if (
        host.get_fact(Command, f"test -d {home}/.bashrc.d/ || echo missing")
        == "missing"
    ):
        files.directory(
            name="Create ~/.bashrc.d/ for organizing bash customizations",
            path=f"{home}/.bashrc.d/",
            user=user,
            # _su_user=user,
        )

    files.block(
        name="Ensure ~/.bashrc sources all the files in ~/.bashrc.d/*",
        path=f"{home}/.bashrc",
        content=dedent(
            """
            if [ -d ~/.bashrc.d ]; then
                shopt -s nullglob  # Make globs expand to nothing if no matches
                for file in ~/.bashrc.d/*; do
                    if [ -f "$file" ]; then  # Check if it's a regular file
                        source "$file"
                    fi
                done
                shopt -u nullglob  # Turn off nullglob when done
            fi
            """
        ),
        _su_user=user,
        try_prevent_shell_expansion=True,  # needed for $file
    )
