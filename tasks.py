#!/usr/bin/env -S uv run --script

"""
You can run this module with invoke (uv tool install invoke) or directly as a script
with `./tasks.py`.

"""
# /// script
# dependencies = [
#   "invoke",
#   "rich",
#   "pdbpp",
# ]
# ///

import ast
import subprocess
import sys
from io import StringIO
from pathlib import Path
from textwrap import dedent

from invoke import Context, Task, task
from invoke.collection import Collection
from invoke.util import debug

config = {"vm": {"name": "dev-deploy-test"}}


@task()
def vm_down(ctx: Context, vm_name: str = "") -> None:
    vm_name = vm_name or ctx.config.vm.name
    ctx.run(f"limactl stop {vm_name}")


@task()
def vm_up(ctx: Context, vm_name: str = "") -> None:
    vm_name = vm_name or ctx.config.vm.name
    ctx.run(f"limactl start {vm_name}")


DOCKERFILE_CONTENTS = dedent(
    """
    # Dockerfile
    FROM rockylinux:9 as builder

    # Install build dependencies
    RUN dnf groupinstall -y "Development Tools" && \
        dnf install -y \
        cmake \
        ncurses-devel \
        pcre2-devel \
        python3-devel \
        gettext-devel \
        which \
        git

    # Clone and build fish
    WORKDIR /src
    RUN git clone https://github.com/fish-shell/fish-shell.git && \
        cd fish-shell && \
        git checkout 3.7.0 && \
        cmake -DCMAKE_INSTALL_PREFIX=/usr/local . && \
        make -j$(nproc)
    """
)


@task()
def build_fish_in_rhel(ctx: Context):
    ctx.run(
        "docker build -f /dev/stdin -t fish_builder .",
        in_stream=StringIO(DOCKERFILE_CONTENTS),
    )


@task(
    autoprint=True,
)
def list_deploys(ctx: Context, where="./src/pysetmeup", query="") -> str:
    """Find all the @deploy decorated functions inside this module, helps"""
    path = Path(where)

    files = list(path.rglob("*.py"))
    output = []
    for file in files:
        debug(file)

        with file.open("r") as f:
            tree = ast.parse(f.read(), filename=file)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.decorator_list:
                    continue
                try:
                    decorators = {dec.func.id for dec in node.decorator_list}
                except AttributeError:
                    continue
                if {"deploy"} & decorators:
                    relative = file.relative_to(path)
                    dotted = str(relative).replace("/", ".").removesuffix(".py")
                    importable_name = f"pysetmeup.{dotted}.{node.name}"
                    debug(f"{file=}")
                    debug(f"{dotted=}")
                    output.append(importable_name)
                    continue
    return "\n".join(output)


@task(autoprint=True)
def select(
    ctx: Context,
    query: str = "",
    multi: bool = False,
    select_1: bool = False,
    one_line: bool = False,
) -> str:
    """Selects a deploy using fzf"""
    arguments = ""
    if query:
        arguments = f"{arguments} --query {query}"
    if multi:
        arguments = f"{arguments} --multi"
    if select_1:
        arguments = f"{arguments} -1"

    fzf = subprocess.run(
        f"uvx invoke list-deploys | fzf {arguments}",
        shell=True,
        stdout=subprocess.PIPE,
    )

    selection = fzf.stdout.decode().strip()
    if not selection:
        sys.exit("No task selected")
    if one_line:
        debug("Making all selections a single line.")
        selection = selection.replace("\n", " ")
    return selection


@task(
    help={
        "inventory": "Where to run the commands, defaults to @local",
        "debug": "Enables pyinfra DEBUG",
        "yes": "Applies operations without confirmation",
        "operation_": "Operations to perform, if not provided will provide a list",
        "query": "When no operation is provided, will show a list of operations to perform",
        "multiple": "Allows to select multiple operations using [Tab] the selector is displayed.",
        "uv_args": "Pass arguments to uv",
        "refresh": "Shorthand for --uv-args --isolated, to force refresh the code",
    }
)
def run_deploy(
    ctx: Context,
    inventory="@local",
    debug=True,
    yes=False,
    operation_: list[str] = [],
    query: str = "",
    multiple=False,
    refresh=False,
    uv_args=[],
) -> None:
    """Runs the operation by default in @local host, and the in"""
    if not operation_:
        operation_ = select(ctx, query=query, multi=multiple).split("\n")
    arguments = ""
    if debug:
        arguments = f"{arguments} --debug"
    if yes:
        arguments = f"{arguments} --yes"
    if refresh and "--refresh" not in uv_args:
        uv_args.append("--refresh")
    uv_args_ = " ".join(uv_args)
    for operation in operation_:
        ctx.run(
            f"uv tool run {uv_args_} --with . pyinfra {inventory} {operation} {arguments}",
            pty=True,
        )


ns = Collection()

for name, element in list(
    locals().items()
):  # list prevent the local iter vars to change the locals
    if isinstance(element, Task):
        if name.count("up"):
            continue

        ns.add_task(element)

ns.configure(config)


if __name__ == "__main__":
    from invoke.program import Program

    p = Program(version="0.0.1", namespace=ns)
    p.run()
