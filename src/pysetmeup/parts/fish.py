from pyinfra import host
from pyinfra.api import deploy


from pyinfra.facts.server import LinuxName, Which, Command
from pyinfra.operations import dnf, server, apt, apk
from pyinfra.operations import files, git


@deploy(name="Install Fish 🐟 shell")
def deploy(version="3.6.0", user=None):
    install = True
    fish_location = host.get_fact(Which, command="fish")
    if fish_location:
        *_, installed_version = host.get_fact(Command, command="fish --version").split(
            " "
        )

        if installed_version >= version:
            install = False

    linux_name = host.get_fact(LinuxName)
    if install:
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
            server.shell(
                name="Install Recent version of fish 🐟 using WebInstaller for user",
                commands=["curl -sS https://webi.sh/fish | sh"],
                _su_user=user,
            )
    if not user:
        # We assume that installation is not in a specific user
        # so we put fish into the available shells
        files.block(
            path="/etc/shells",
            content=fish_location,
            _su_user="root",
        )


if __name__ in {"builtins", "__main__"}:
    deploy()
