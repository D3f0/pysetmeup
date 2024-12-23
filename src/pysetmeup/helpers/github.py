from pathlib import Path
import requests
import tarfile
import zipfile
from typing import Optional, List
import shutil
import tempfile
import platform
import sys


def get_system_info() -> dict:
    """
    Get current system's architecture and OS information.
    Returns a dict with normalized platform information.
    """
    arch_map = {
        "x86_64": ["x86_64", "x64", "amd64"],
        "aarch64": ["arm64", "aarch64", "arm"],
        "i386": ["386", "i386", "x86"],
    }

    os_map = {
        "Linux": ["linux", "ubuntu", "debian"],
        "Darwin": ["darwin", "mac", "macos"],
        "Windows": ["windows", "win"],
    }

    system = platform.system()
    machine = platform.machine().lower()

    # Determine architecture
    detected_arch = None
    for arch, variants in arch_map.items():
        if any(variant in machine for variant in variants):
            detected_arch = arch
            break

    return {
        "os": system,
        "os_patterns": os_map.get(system, []),
        "arch": detected_arch or machine,
        "arch_patterns": next(
            (
                patterns
                for arch, patterns in arch_map.items()
                if any(variant in machine for variant in patterns)
            ),
            [],
        ),
        "is_64bit": sys.maxsize > 2**32,
    }

import hunter

@hunter.wrap()
def score_asset(asset_name: str, system_info: dict) -> int:
    """
    Score an asset based on how well it matches the current system.
    Higher score means better match.
    """
    name = asset_name.lower()
    score = 0

    # Check OS match
    if any(os_pattern in name for os_pattern in system_info["os_patterns"]):
        score += 100

    # Check architecture match
    if any(arch_pattern in name for arch_pattern in system_info["arch_patterns"]):
        score += 50
    elif system_info["is_64bit"] and "64" in name:
        score += 30

    # Prefer certain formats
    if system_info["os"] == "Windows" and name.endswith(".zip"):
        score += 10
    elif system_info["os"] in ["Linux", "Darwin"] and name.endswith(".tar.gz"):
        score += 10

    return score


def download_release_binary(
    repo: str,
    version: Optional[str] = "latest",
    output_dir: str = "downloads",
    binary_pattern: Optional[str] = None,
) -> Path:
    """
    Download and extract binaries from GitHub release assets using a temporary directory.
    Automatically selects the most appropriate binary for the current system.

    Args:
        repo: GitHub repository in format "owner/repo"
        version: Release version (e.g., "v1.0.0", "latest")
        output_dir: Directory to save the final binary files
        binary_pattern: Optional pattern to match binary files (e.g., '*.exe' or 'program')

    Returns:
        Path: Path to the extracted binary file or directory

    Raises:
        ValueError: If repo format is invalid or no suitable assets are found
    """
    # Validate and parse repo format
    if "/" not in repo:
        raise ValueError('Repository must be in format "owner/repo"')
    owner, repo_name = repo.split("/", 1)

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Get system information
    system_info = get_system_info()

    # Construct GitHub API URL
    if version == "latest":
        release_url = (
            f"https://api.github.com/repos/{owner}/{repo_name}/releases/latest"
        )
    else:
        # Remove 'v' prefix if present for consistency
        version = version.lstrip("v")
        release_url = (
            f"https://api.github.com/repos/{owner}/{repo_name}/releases/tags/v{version}"
        )

    # Get release information
    headers = {
        "Accept": "application/vnd.github.v3+json",
        # Add GitHub token if needed:
        # "Authorization": f"token {os.environ['GITHUB_TOKEN']}"
    }

    response = requests.get(release_url, headers=headers)
    response.raise_for_status()
    release_data = response.json()

    # Score and sort assets
    scored_assets = [
        (asset, score_asset(asset["name"], system_info))
        for asset in release_data["assets"]
        if asset["content_type"]
        in ["application/x-gzip", "application/zip", "application/octet-stream"]
    ]
    scored_assets.sort(key=lambda x: x[1], reverse=True)

    if not scored_assets:
        raise ValueError("No suitable release assets found for your system")

    print(
        f"Selected asset: {scored_assets[0][0]['name']} (score: {scored_assets[0][1]})"
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        asset = scored_assets[0][0]

        # Download the asset to temp directory
        asset_url = asset["browser_download_url"]
        local_path = temp_path / asset["name"]

        print(f"Downloading {asset_url}...")
        response = requests.get(asset_url, headers=headers, stream=True)
        response.raise_for_status()

        local_path.write_bytes(response.content)

        # Extract the archive in temp directory
        extract_path = temp_path / "extracted"
        extract_path.mkdir(exist_ok=True)

        if asset["name"].endswith(".tar.gz"):
            with tarfile.open(local_path, "r:gz") as tar:
                tar.extractall(extract_path)
        elif asset["name"].endswith(".zip"):
            with zipfile.ZipFile(local_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
        elif not binary_pattern:  # Direct binary download
            shutil.copy2(local_path, output_path / local_path.name)
            return output_path / local_path.name

        # Find and copy the binary to the final output directory
        if binary_pattern:
            for file_path in extract_path.rglob("*"):
                if binary_pattern in file_path.name and file_path.is_file():
                    dest = output_path / file_path.name
                    shutil.copy2(file_path, dest)
                    return dest
        else:
            # If no pattern specified, copy all files to output directory
            for file_path in extract_path.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(extract_path)
                    dest = output_path / rel_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest)
            return output_path

    raise ValueError("No suitable binaries found in the release assets")


# Example usage
if __name__ == "__main__":
    try:
        binary_path = download_release_binary(
            repo="sharkdp/fd",  # Now using single string format
            version="latest",  # or specific version like "v8.7.0"
            binary_pattern="fd",
            output_dir="downloads",
        )
        print(f"Binary extracted to: {binary_path}")
    except Exception as e:
        print(f"Error: {e}")
