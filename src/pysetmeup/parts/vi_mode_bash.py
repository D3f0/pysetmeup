import io
from textwrap import dedent

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import Command, Home, User
from pyinfra.operations import files

CONTENT = dedent(
    """
    set editing-mode vi
    $if mode=vi

    set keymap vi-command
    # these are for vi-command mode
    Control-l: clear-screen

    set keymap vi-insert
    # these are for vi-insert mode
    Control-l: clear-screen
    $endif
    """
).strip()


@deploy(name="Set Ctrl+L mode in bash once you're in vi mode")
def deploy():
    """

    Source: https://unix.stackexchange.com/questions/104094/is-there-any-way-to-enable-ctrll-to-clear-screen-when-set-o-vi-is-set
    """
    home = host.get_fact(Home)
    user = host.get_fact(User)
    path = f"{home}/.inputrc"
    file_status = host.get_fact(Command, command=f'test -f {path} || echo "MISSING"')
    if file_status == "MISSING":
        inputrc = ""
    else:
        inputrc = host.get_fact(Command, command=f"cat {path}")
    if not inputrc or CONTENT not in inputrc:
        new_content = f"{inputrc}\n{CONTENT}"
        src = io.StringIO(new_content)
        files.put(src=src, dest=path, user=user)

    # files.block(
    #     path=f"{home}/.inputrc",
    #     marker="## {mark} vi mode clear screen ##",
    #     try_prevent_shell_expansion=True,
    #     content=dedent(
    #         """
    #         set editing-mode vi
    #         $if mode=vi

    #         set keymap vi-command
    #         # these are for vi-command mode
    #         Control-l: clear-screen

    #         set keymap vi-insert
    #         # these are for vi-insert mode
    #         Control-l: clear-screen
    #         $endif
    #         """
    #     )
    # )


if __name__ in {"builtins", "__main__"}:
    deploy()
