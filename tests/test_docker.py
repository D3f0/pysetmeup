import pytest
import subprocess
from loguru import logger
from functools import partial

images_to_test = {
    "centos": "quay.io/centos/centos:stream9",
    "alpine": "alpine",
}


def dispose_container(container_id: str) -> None:
    logger.info(f"Disposing container {container_id}")
    subprocess.call(f"docker rm -f {container_id}".split())


@pytest.mark.parametrize("image", images_to_test.values(), ids=images_to_test.keys())
def test_multiple_distros(request, image, top_level):
    command = (
        # f"docker run -d --rm -ti -w /code -v {top_level}:/code {image}  sh -c 'sleep infinity'",
        f"docker run -d --rm -ti {image}  sh -c 'sleep infinity'",
    )
    logger.debug(f"{command=}")
    docker_detached = subprocess.run(
        command,
        shell=True,
        cwd=top_level,
        capture_output=True,
    )
    assert docker_detached.returncode == 0, f"{command} failed"

    container_id = docker_detached.stdout.decode().strip()
    request.addfinalizer(partial(dispose_container, container_id))
    proc = subprocess.run(
        f"uv run pyinfra @docker/{container_id} pysetmeup.deploys.rclone.install --debug-all -y",
        shell=True,
        cwd=top_level,
    )
    assert proc.returncode == 0
