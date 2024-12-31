"""
LV Logical Volume used by a LXC container
VG a grouping of physical volume
PV a physical volume

┌───────────────┐  ┌───────────────┐ ┌───────────────┐
│               │  │               │ │               │
│      LV       │  │       LV      │ │       LV      │
│               │  │               │ │               │
└───────────────┘  └───────────────┘ └───────────────┘
┌────────────────────────────────────────────────────┐
│                                                    │
│                        VG                          │
│                                                    │
└────────────────────────────────────────────────────┘
┌───────────────┐  ┌───────────────┐ ┌───────────────┐
│               │  │               │ │               │
│      PV       │  │       PV      │ │       PV      │
│               │  │               │ │               │
└───────────────┘  └───────────────┘ └───────────────┘

Host data:
"vg_name": str # defaults to vg1
"""

import json
from typing import TypedDict
from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName, Command
from pyinfra.operations import server
from pyinfra import logger


class BlockdeviceChildDict(TypedDict):
    name: str
    # "maj:min": str
    rm: bool
    size: str
    ro: bool
    type: str
    mountpoint: str | None
    children: list["BlockdeviceChildDict"] | None


class BlockdeviceDict(TypedDict):
    name: str
    # "maj:min": str
    rm: bool
    size: str
    ro: bool
    type: str
    mountpoints: str | None
    children: list[BlockdeviceChildDict] | None


class LsblkDict(TypedDict):
    blockdevices: list[BlockdeviceDict]


@deploy(name="Install LVM in RedHat")
def deploy_lvm_in_redhat():
    if (
        host.get_fact(Command, command="rpm -qa | grep lvm2 || echo missing")
        == "missing"
    ):
        server.dnf.packages("lvm2")
    else:
        logger.info("lmv2 already present")


@deploy(name="Install LVM in Debian")
def deploy_lvm_in_debian():
    if (
        host.get_fact(Command, command="dpkg -l | grep lvm2 || echo missing")
        == "missing"
    ):
        server.apt.packages("lvm2")
    else:
        logger.info("lmv2 already present")


def get_vgcreate_devices() -> list[BlockdeviceDict]:
    """Find partitions to use for pvcreate"""
    blkid_json_output = host.get_fact(Command, command="lsblk -J")
    blkid_output: LsblkDict = json.loads(blkid_json_output)
    blockdevices = blkid_output["blockdevices"]
    targets = []
    for blockdevice in blockdevices:
        if blockdevice.get("children"):
            logger.info(f"Ignoring {blockdevice} because of children property")
            continue

        mountpoints = blockdevice.get("mountpoints", [])
        if mountpoints and mountpoints != [None]:
            logger.info(f"Ignoring {blockdevice} because it's already mounted")
            continue

        targets.append(blockdevice)

    return targets


@deploy(name="Install LVM and ensure a VG is available")
def deploy():
    linux_name = host.get_fact(LinuxName)
    if not linux_name:
        logger.warning("Can't install LVM in non linux OS")
        return
    if linux_name == "RedHat":
        deploy_lvm_in_redhat()
    elif linux_name == "Debian":
        deploy_lvm_in_debian()
    else:
        logger.warning(f"Don't know how to install lvm in {linux_name}")
    vg_name = host.data.get("vg_name", "vg1")
    vgs = host.get_fact(Command, command="vgs") or ""
    if vg_name in vgs:
        logger.info(f"Volume Group {vg_name} already exists")
        return

    devices = get_vgcreate_devices()
    args = " ".join(f"/dev/{dev['name']}" for dev in devices)
    command = f"vgcreate {vg_name} {args}"
    logger.info(f"{command=}")
    server.shell(name="Run vgcreate", commands=[command])


if __name__ in {"builtins", "__main__"}:
    deploy()
