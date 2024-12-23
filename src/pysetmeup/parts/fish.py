from pyinfra import host
from pyinfra.api import deploy


from pyinfra.facts.server import LinuxName, Which, Command
from pyinfra.operations import dnf, server, apt, apk
from pyinfra.operations import files, git


@deploy(name="🐟 shell")
def deploy(version="3.6.0"):
    if not host.get_fact(Which, command="fish"):
        *_, installed_version = host.get_fact(Command, "fish --version").split(" ")
        if installed_version >= version:
            return
    linux_name = host.get_fact(LinuxName)
    if host.get_fact(LinuxName) == "RedHat":
        server.shell('dnf groupinstall -y "Development Tools"')
        dnf.packages(
            [
                "cmake",
                "ncurses-devel",
                "pcre2-devel",
                "python3-devel",
                "gettext-devel",
                "which",
                "git",
            ],
        )
        files.directory("/src")
        git.repo(
            "https://github.com/fish-shell/fish-shell.git",
            "/src/fish-shell",
            branch="3.7.0",
        )
        # Compile and install
        server.shell(
            [
                "cd /src/fish-shell/ && "
                "cmake -DCMAKE_INSTALL_PREFIX=/usr/local . && "
                "make -j$(nproc) && "
                "make install"
            ],
        )
    elif linux_name == "Debian":
        apt.packages(["fish"])
    elif linux_name == "Alpine":
        apk.packages(["fish"])
    else:
        raise LookupError("Don't know how to install fish in ")


if __name__ in {"builtins", "__main__"}:
    deploy()
