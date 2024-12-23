# pyinfra deploy.py <hostname>
from pyinfra.operations import server


server.shell(
    name="Set linuxbrew",
    commands=[
        """
        bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        """
    ],
    _su_user="nahuel",
)
