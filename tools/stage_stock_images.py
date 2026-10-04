#!/usr/bin/env python3
"""Copy verified stock images and metadata inputs into the device tree."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_sha256(root: Path) -> tuple[int, str]:
    """Hash sorted relative paths and each file's SHA-256 digest."""
    files = sorted(path for path in root.rglob("*") if path.is_file())
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256(path)))
    return len(files), digest.hexdigest()


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    default_destination = project_root / "crdroid/device/motorola/vienna/prebuilts"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=default_destination)
    args = parser.parse_args()

    lock = json.loads((project_root / "sources.lock.json").read_text(encoding="utf-8"))
    if (
        lock["device"]["sku"] != "XT2409-1"
        or lock["device"]["carrier"] != "reteu"
        or lock["firmware"]["build"] != "W1UIS36H.39-25-8"
    ):
        raise ValueError("source lock does not describe the expected XT2409-1 RETEU stock build")

    args.destination.mkdir(parents=True, exist_ok=True)
    artifacts = list(lock["prebuilt_images"].items()) + list(
        lock.get("prebuilt_build_props", {}).items()
    )
    for artifact_name, artifact in artifacts:
        source = project_root / artifact["source"]
        destination = args.destination / artifact_name
        if not source.is_file():
            raise FileNotFoundError(source)
        if sha256(source) != artifact["sha256"]:
            raise ValueError(f"stock image checksum mismatch: {source}")
        if destination.exists():
            if sha256(destination) != artifact["sha256"]:
                raise ValueError(f"staged image checksum mismatch: {destination}")
            print(f"Already verified: {artifact_name}")
            continue
        shutil.copyfile(source, destination)
        if sha256(destination) != artifact["sha256"]:
            raise ValueError(f"copy verification failed: {destination}")
        print(f"Staged: {artifact_name}")

    for directory_name, artifact in lock.get("prebuilt_vintf_dirs", {}).items():
        source = project_root / artifact["source"]
        destination = args.destination / directory_name
        if not source.is_dir():
            raise FileNotFoundError(source)
        expected = (artifact["file_count"], artifact["sha256"])
        if tree_sha256(source) != expected:
            raise ValueError(f"stock VINTF checksum mismatch: {source}")
        if destination.exists():
            if tree_sha256(destination) != expected:
                raise ValueError(f"staged VINTF checksum mismatch: {destination}")
            print(f"Already verified: {directory_name}")
            continue
        shutil.copytree(source, destination)
        if tree_sha256(destination) != expected:
            raise ValueError(f"VINTF copy verification failed: {destination}")
        print(f"Staged: {directory_name}")


if __name__ == "__main__":
    main()
