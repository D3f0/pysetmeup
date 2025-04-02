"""
To run this deploy alone you can use uv as:

```
uv run pyinfra <target> pysetmeup.parts.lxc.deploy --debug
```

"""

import re
from textwrap import dedent

from pyinfra import host, logger
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName, Command
from pyinfra.operations import dnf, server, files

ifcfg_lxcbr_content = dedent("""
# Add configuration
DEVICE=lxcbr0
TYPE=Bridge
ONBOOT=yes
BOOTPROTO=static
IPADDR=10.0.3.1
NETMASK=255.255.255.0
""").strip()


@deploy(name="Setup LXC")
def deploy():
    from .epel import install_epel_repositories

    install_epel_repositories()

    linux_name = host.get_fact(LinuxName)
    if not linux_name:
        logger.warning("lxc can only be installed in Linux hosts")
    if linux_name == "RedHat":
        installed = host.get_fact(Command, "rpm -qa").splitlines()
        installed_dict: dict[str, str] = dict(
            re.split(r"-\d", line, maxsplit=1) for line in installed if line
        )
        required_packages: list[str] = [
            "epel-release",
            "lxc",
            "lxc-libs",
            "lxc-templates",
            "libvirt",
            "debootstrap",
            "wget",
            "rsync",
            "bridge-utils",
            "dnsmasq",
        ]

        packages = [pkg for pkg in required_packages if pkg not in installed_dict]
        if packages:
            dnf.packages(
                packages,
                # https://fedoraproject.org/wiki/LXC
                name="Installing dependencies",
            )
        else:
            logger.info("All required packages for LXC installed")
        server.shell("systemctl enable --now libvirtd", name="Enabling libvirtd")
        server.shell("systemctl enable --now lxc", name="Enabling lxc")
        # # TODO check idempotency
        # files.block(
        #     "/etc/sysconfig/network-scripts/ifcfg-lxcbr0",
        #     ifcfg_lxcbr_content,
        # )
        files.block(
            "/etc/sysconfig/lxc",
            'USE_LXC_BRIDGE="true"',
        )
        server.shell("systemctl enable --now lxc-net.service", name="Enabling lxc-net")
        files.block("/etc/sysctl.d/lxc.conf", "net.ipv4.ip_forward=1")
        server.shell(
            name="Enabling forwarding", commands="sysctl -p /etc/sysctl.d/lxc.conf"
        )
        # server.shell(
        #     name="Updating firewall",
        #     commands=[
        #         "firewall-cmd --permanent --direct --add-rule ipv4 filter FORWARD 0 -i lxcbr0 -j ACCEPT",
        #         "firewall-cmd --permanent --direct --add-rule ipv4 nat POSTROUTING 0 -s 10.0.3.0/24 -j MASQUERADE",
        #         "firewall-cmd --reload",
        #     ],
        # )


if __name__ == {"builtins", "__main__"}:
    deploy()
