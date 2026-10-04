#!/usr/bin/env python3
"""Fetch one Git LFS pointer without requiring git-lfs on the host."""

import argparse
import configparser
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.request import Request, urlopen


POINTER = re.compile(
    r"version https://git-lfs.github.com/spec/v1\n"
    r"oid sha256:([0-9a-f]{64})\n"
    r"size ([0-9]+)\n?"
)


def fetch(path: Path) -> None:
    pointer = path.read_text(encoding="ascii")
    match = POINTER.fullmatch(pointer)
    if not match:
        raise ValueError(f"Not a Git LFS pointer: {path}")
    oid, expected_size = match.group(1), int(match.group(2))

    config = configparser.ConfigParser()
    if not config.read(path.parent / ".lfsconfig"):
        raise FileNotFoundError(f"Missing .lfsconfig beside {path}")
    endpoint = config["lfs"]["url"].strip().strip('"').rstrip("/") + "/objects/batch"
    if not endpoint.startswith("https://"):
        raise ValueError("The Git LFS endpoint must use HTTPS")

    request = Request(
        endpoint,
        data=json.dumps(
            {"operation": "download", "transfers": ["basic"],
             "objects": [{"oid": oid, "size": expected_size}]}
        ).encode("utf-8"),
        headers={"Accept": "application/vnd.git-lfs+json",
                 "Content-Type": "application/vnd.git-lfs+json"},
    )
    with urlopen(request, timeout=30) as response:
        obj = json.load(response)["objects"][0]
    if obj.get("oid") != oid or obj.get("size") != expected_size:
        raise ValueError("LFS server returned a different object")
    if "error" in obj:
        raise RuntimeError(f"LFS server error: {obj['error']}")
    download = obj["actions"]["download"]
    if not download["href"].startswith("https://"):
        raise ValueError("The Git LFS download must use HTTPS")

    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".lfs-download-",
                                         delete=False) as output:
            temporary = Path(output.name)
            digest = hashlib.sha256()
            size = 0
            with urlopen(Request(download["href"], headers=download.get("header", {})),
                         timeout=60) as response:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
        if size != expected_size or digest.hexdigest() != oid:
            raise ValueError("Downloaded LFS object failed size or SHA-256 verification")
        os.chmod(temporary, 0o644)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f"Fetched and verified {path} ({size} bytes, sha256:{oid})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pointer", type=Path)
    fetch(parser.parse_args().pointer)
