import getpass

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files
from textwrap import dedent


@deploy(name="Create ~/.bashrc.d directory")
def deploy():
    user = host.data.get("user", getpass.getuser())

    files.directory(
        name="Create ~/.bashrc.d/ for organizing bash customizations",
        path=f"/home/{user}/.bashrc.d/",
        user=user,
        _su_user=user,
    )

    files.block(
        name="Ensure ~/.bashrc sources all the files in ~/.bashrc.d/*",
        path=f"/home/{user}/.bashrc",
        content=dedent(
            """
            if [ -d ~/.bashrc.d ]; then
                    for file in ~/.bashrc.d/*; do
                            source $file
                    done
            fi
            """
        ),
        _su_user=user,
    )
