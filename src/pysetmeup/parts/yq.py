from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import Which, LinuxDistribution


from pyinfra.operations import apt, apk, brew, server
from ..helpers.github import download_release_binary


@deploy("yq")
def deploy():
    if host.get_fact(Which, "yq"):
        return
    os = host.get_fact(server.Os)

    if os == "Darwin":
        # MacOS installation using Homebrew
        brew.packages(
            name="Install yq via Homebrew",
            packages=["yq"],
        )

    elif os == "Linux":
        distribution_name = host.get_fact(LinuxDistribution)["name"]

        if distribution_name in ["Debian", "Ubuntu", "Raspbian"]:
            apt.packages(
                name="Install yq via apt",
                packages=["yq"],
                update=True,
            )

        elif distribution_name in ["RedHat", "CentOS", "CentOS Stream", "Fedora"]:
            # Not in EPEL repository, need to download binary, using WebInstaller
            download_release_binary(repo="mikefarah/yq", output_dir="/usr/local/bin/")

        elif distribution_name == "Alpine":
            # Alpine Linux installation
            apk.packages(
                name="Install yq via apk",
                packages=["yq"],
                update=True,
            )


if __name__ in {"builtins", "__main__"}:
    deploy()
