from io import StringIO
from textwrap import dedent
from pyinfra.api import deploy
from pyinfra import host, logger
from . import lxc
from pyinfra.operations import server, files
from pyinfra.facts.server import Command


@deploy(name="Setup LXC containers with LVM backingstore")
def deploy():
    """
    Creates an LXC container based by LVM partition.

    An example of the host data:
    ```
    app_servers = [("host", {"lxc_containers": [{"name": "ubuntu"}]})]
    ```


    """
    containers: list[dict] = host.data.get("lxc_containers")
    if containers:
        lxc.deploy()
    for container in containers:
        name = container.get("name")
        if not name:
            logger.warning(
                f"Skipping container config {container} because of missing name"
            )
            continue
        create = (
            host.get_fact(Command, f"lxc-ls -1 | grep {name} || echo missing")
            == "missing"
        )
        init_script = container.get("init_script", "")
        if create:
            distro = container.get("distro", "ubuntu")
            release = container.get("release", "focal")
            arch = container.get("arch", "amd64")
            volume_group = container.get("volume_group")
            size = container.get("size", "50G")
            if not volume_group:
                volume_group = host.get_fact(
                    Command, "vgs --noheadings -o vg_name"
                ).strip()

            command = dedent(f"""
                lxc-create -n {name} -t download -B lvm
                    --lvname rootfs-{name} \
                    --vgname {volume_group} \
                    --fssize {size} \
                    -- \
                    --dist {distro} \
                    --release {release} \
                    --arch {arch}

            """).replace("\n", " ")
            server.shell(command, name=f"Creating LXC container {name}")

        nesting = container.get("nesting", True)
        if nesting:
            files.line(
                f"/var/lib/lxc/{name}/config",
                "lxc.include = /usr/share/lxc/config/nesting.conf",
                name="Enable nesting (support for Docker)",
            )
        # Start the container if already created
        server.shell(f"lxc-start {name}", name=f"Staring container {name}")

        # If the init script is present, run it
        if init_script:
            tmp_path = host.get_fact(Command, "mktemp")
            files.put(StringIO(init_script), tmp_path, name="Setting the init script")
            server.shell(f"cat {tmp_path} | lxc-attach {name} -- bash")
