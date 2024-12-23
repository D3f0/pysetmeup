from pathlib import Path
from collections.abc import Callable
import pytest
import subprocess
import shlex
import docker
from loguru import logger


@pytest.fixture
# @functools.lru_cache()
def top_level() -> Path:
    """Returns the top of the repo"""
    toplevel = (
        subprocess.check_output("git rev-parse --show-toplevel".split())
        .decode()
        .strip()
    )
    toplevel = Path(toplevel)
    return toplevel


@pytest.fixture()
def start_container(request) -> Callable[[str], str]:
    def _start_container(image):
        image = "alpine"
        proc = subprocess.run(
            shlex.split(f"docker run --rm -d {image} -- sh -c 'sleep infinity'"),
            capture_output=True,
        )
        return proc.stdout.decode().strip()

    return _start_container


@pytest.fixture()
def docker_env() -> docker.DockerClient:
    """Entry point for docker daemon environment"""
    return docker.from_env()


@pytest.fixture
def create_container(
    docker_env,
    top_level,
):
    def _create_container(
        image,
        command=None,
        detach=False,
        remove=True,
        env=None,
    ):
        # Configure your container
        command = command or ["sh", "-xc", "./run.sh"]
        volumes = {top_level: {"bind": "/code", "mode": "ro"}}
        logger.debug(f"{command=} {volumes=}")
        container = docker_env.containers.run(
            image=image,
            command=command,
            detach=detach,
            remove=remove,
            environment=env,
            volumes=volumes,
            working_dir="/code",
            platform=None,
        )
        return container

    return _create_container
