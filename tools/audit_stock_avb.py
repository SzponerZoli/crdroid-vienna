#!/usr/bin/env python3
"""Record stock AVB metadata and compare its key with the prototype key."""

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AVBTOOL = ROOT / "crdroid/external/avb/avbtool.py"
STOCK = ROOT / "stock-firmware/extracted"
TEST_KEY = ROOT / "crdroid/external/avb/test/data/testkey_rsa2048.pem"
OUTPUT = ROOT / "research/avb-stock.json"


def field(output: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:\s+(.+)$", output, re.MULTILINE)
    if match is None:
        raise ValueError(f"Missing AVB field: {name}")
    return match.group(1).strip()


def image_info(name: str) -> dict:
    result = subprocess.run(
        ["python3", str(AVBTOOL), "info_image", "--image", str(STOCK / name)],
        capture_output=True,
        text=True,
        check=True,
    )
    output = result.stdout
    chains = [
        {"partition": partition, "rollback_index_location": int(location)}
        for partition, location in re.findall(
            r"Chain Partition descriptor:\n\s+Partition Name:\s+(\S+)\n"
            r"\s+Rollback Index Location:\s+(\d+)",
            output,
        )
    ]
    return {
        "image": name,
        "algorithm": field(output, "Algorithm"),
        "public_key_sha1": field(output, "Public key (sha1)"),
        "rollback_index": int(field(output, "Rollback Index")),
        "header_rollback_index_location": int(field(output, "Rollback Index Location")),
        "chain_partitions": chains,
        "described_partitions": sorted(set(re.findall(r"Partition Name:\s+(\S+)", output))),
    }


def key_sha1(key: Path) -> str:
    with tempfile.TemporaryDirectory() as temporary:
        public_key = Path(temporary) / "avbpubkey"
        subprocess.run(
            [
                "python3",
                str(AVBTOOL),
                "extract_public_key",
                "--key",
                str(key),
                "--output",
                str(public_key),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return hashlib.sha1(public_key.read_bytes()).hexdigest()


def main() -> None:
    root = image_info("vbmeta.img")
    child = image_info("vbmeta_system.img")
    prototype_key_sha1 = key_sha1(TEST_KEY)
    report = {
        "method": "avbtool info_image from exact-model stock images",
        "stock_root_vbmeta": root,
        "stock_vbmeta_system": child,
        "prototype_test_key_sha1": prototype_key_sha1,
        "prototype_key_matches_stock": prototype_key_sha1 == root["public_key_sha1"],
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Stock key matches prototype test key: {report['prototype_key_matches_stock']}")
    print(OUTPUT)


if __name__ == "__main__":
    main()
