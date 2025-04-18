from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import Which, LinuxName, Home
from pyinfra.operations import server, dnf


@deploy(name="Install Starship prompt 🚀")
def deploy(user: str | None = ""):
    starship_location = host.get_fact(Which, "starship")

    if not starship_location:
        linux_name = host.get_fact(LinuxName)

        if linux_name == "RedHat":
            server.shell(
                "dnf copr list | grep starship || dnf copr enable atim/starship --yes"
            )
            dnf.packages("starship")
        else:
            server.shell("curl -sS https://starship.rs/install.sh | sh -- --yes")

    user = user or host.data.get("user")
    home = host.get_fact(Home, user=user)
    server.shell(
        f"starship init bash > {home}/.bashrc.d/99_starship.sh",
        name="Setting init script in bash2",
        _su_user=user,
    )


if __name__ in {"builtins", "__main__"}:
    deploy()
