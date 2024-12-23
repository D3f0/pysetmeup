from io import StringIO
import json
from pathlib import Path
import subprocess
from textwrap import dedent
from typing import Optional
from invoke import task, Context, Task, Result
from invoke.collection import Collection


config = {"vm": {"name": "dev-deploy-test"}}


@task()
def vm_down(ctx: Context, vm_name: str = "") -> None:
    breakpoint()
    vm_name = vm_name or ctx.config.vm.name
    ctx.run(f"limactl stop {vm_name}")


@task()
def vm_up(ctx: Context, vm_name: str = "") -> None:
    vm_name = vm_name or ctx.config.vm.name
    ctx.run(f"limactl start {vm_name}")


# @task()
# def run(ctx: Context, where: str = "", what: str = "", query=False) -> None:
#     if not where or query:
#         options = ctx.run(
#             "grep -R '^Host' ~/.ssh/ | grep -v '*' | awk '{print $2}'"
#         ).stdout.strip().splitlines()

#         host = iterfzf(options, sort=True, query=query and f"{where}")
#     if not what or query :
#         options = list(str(p) for p in Path(".").glob("src/setups"))
#         iterfzf(options, sort=True, query=query and host)


@task(
    help={
        "verbose": "Print meta (-v), input (-vv) and output (-vvv)",
        "dry": "Don't execute operations on the target hosts",
        "yes": "Execute operations immediately without prompt or checking for changes",
        "limit": "Restrict the target hosts by name and group name",
        "fail_percent": "% of hosts that need to fail before exiting early",
        "data": "Override data values, format key=value",
        "group_data": "Paths to load additional group data from (overrides matching keys)",
        "config": "Specify config file to use (default: config.py)",
        "chdir": "Set the working directory before executing",
        "sudo": "Whether to execute operations with sudo",
        "sudo_user": "Which user to sudo when sudoing",
        "use_sudo_password": "Whether to use a password with sudo",
        "su_user": "Which user to su to",
        "shell_executable": 'Shell to use (ex: "sh", "cmd", "ps")',
        "parallel": "Number of operations to run in parallel",
        "no_wait": "Don't wait between operations for hosts",
        "serial": "Run operations in serial, host by host",
        "ssh_user": "SSH user to connect as",
        "ssh_port": "SSH port to connect to",
        "ssh_key": "SSH Private key filename",
        "ssh_key_password": "SSH Private key password",
        "ssh_password": "SSH password",
        "debug": "Print debug logs from pyinfra",
        "debug_all": "Print debug logs from all packages including pyinfra",
        "debug_facts": "Print facts after generating operations and exit",
        "debug_operations": "Print operations after generating and exit",
    },
    positional=["inventory", "operations"],
)
def pyinfra(
    ctx: Context,
    invenotry,
    operations,
    verbose: int = 0,
    dry: bool = False,
    yes: bool = False,
    limit: Optional[str] = None,
    fail_percent: Optional[int] = None,
    data: Optional[str] = None,
    group_data: Optional[str] = None,
    config: str = "config.py",
    chdir: Optional[str] = None,
    sudo: bool = False,
    sudo_user: Optional[str] = None,
    use_sudo_password: bool = False,
    su_user: Optional[str] = None,
    shell_executable: Optional[str] = None,
    parallel: Optional[int] = None,
    no_wait: bool = False,
    serial: bool = False,
    ssh_user: Optional[str] = None,
    ssh_port: Optional[int] = None,
    ssh_key: Optional[Path] = None,
    ssh_key_password: Optional[str] = None,
    ssh_password: Optional[str] = None,
    debug: bool = False,
    debug_all: bool = False,
    debug_facts: bool = False,
    debug_operations: bool = False,
):
    args = []

    # Handle verbose flag specially (-v, -vv, -vvv)
    if verbose > 0:
        args.append("-" + "v" * verbose)

    # Boolean flags
    if dry:
        args.append("--dry")
    if yes:
        args.append("--yes")
    if sudo:
        args.append("--sudo")
    if use_sudo_password:
        args.append("--use-sudo-password")
    if no_wait:
        args.append("--no-wait")
    if serial:
        args.append("--serial")
    if debug:
        args.append("--debug")
    if debug_all:
        args.append("--debug-all")
    if debug_facts:
        args.append("--debug-facts")
    if debug_operations:
        args.append("--debug-operations")

    # Optional value arguments
    if limit:
        args.append(f"--limit {limit}")
    if fail_percent is not None:
        args.append(f"--fail-percent {fail_percent}")
    if data:
        args.append(f"--data {data}")
    if group_data:
        args.append(f"--group-data {group_data}")
    if config and config != "config.py":  # Only add if non-default
        args.append(f"--config {config}")
    if chdir:
        args.append(f"--chdir {chdir}")
    if sudo_user:
        args.append(f"--sudo-user {sudo_user}")
    if su_user:
        args.append(f"--su-user {su_user}")
    if shell_executable:
        args.append(f"--shell-executable {shell_executable}")
    if parallel is not None:
        args.append(f"--parallel {parallel}")
    if ssh_user:
        args.append(f"--ssh-user {ssh_user}")
    if ssh_port is not None:
        args.append(f"--ssh-port {ssh_port}")
    if ssh_key:
        args.append(f"--ssh-key {ssh_key}")
    if ssh_key_password:
        args.append(f"--ssh-key-password {ssh_key_password}")
    if ssh_password:
        args.append(f"--ssh-password {ssh_password}")
    options = " ".join(args)
    ctx.run(f"uv run pyinfra {invenotry} {operations} {options}")


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

@task()
def cat(ctx: Context):
    ctx.run("cat -n", in_stream=StringIO(DOCKERFILE_CONTENTS))

ns = Collection()

for name, element in list(
    locals().items()
):  # list prevent the local iter vars to change the locals
    if isinstance(object, Task):
        if name.count("up"):
            continue
        ns.add_task(element)

ns.configure(config)
