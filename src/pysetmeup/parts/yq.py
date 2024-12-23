from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts


from pyinfra.operations import apt, yum, apk, brew
from pyinfra.facts import server


@deploy("yq")
def install():
    # Detect the operating system
    os = host.get_fact(server.LinuxDistribution)

    if host.get_fact(server_facts.Which, "yq"):
        return

    if host.get_fact(server_facts.Os) == "Darwin":
        # MacOS installation using Homebrew
        brew.packages(
            name="Install yq via Homebrew",
            packages=["yq"],
        )

    elif os:
        distribution = os.get("name", "").lower()

        if distribution in ["debian", "ubuntu", "raspbian"]:
            apt.packages(
                name="Install yq via apt",
                packages=["yq"],
                update=True,
            )

        elif distribution in ["rhel", "centos", "fedora"]:
            # Install EPEL repository first for RedHat-based systems
            yum.packages(
                name="Install EPEL repository",
                packages=["epel-release"],
            )

            yum.packages(
                name="Install yq via yum",
                packages=["yq"],
            )

        elif distribution == "alpine":
            # Alpine Linux installation
            apk.packages(
                name="Install yq via apk",
                packages=["yq"],
                update=True,
            )
