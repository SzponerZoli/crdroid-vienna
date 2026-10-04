#!/usr/bin/env python3
"""Index device-facing files from extracted stock EROFS partitions.

This is a research inventory, not a ready-made proprietary-files.txt. The
generated paths still need curation against the crDroid build and stock HAL
dependencies before being copied into a vendor tree.
"""

import argparse
import json
from pathlib import Path


PARTITIONS = (
    "system",
    "system_ext",
    "product",
    "vendor",
    "system_dlkm",
    "vendor_dlkm",
)
CATEGORIES = (
    "hal_services",
    "hal_libraries",
    "vintf",
    "init_configs",
    "kernel_modules",
    "firmware",
    "permissions",
)


def categories_for(relative: Path) -> tuple[str, ...]:
    parts = relative.parts
    matches = []
    if len(parts) >= 2 and parts[:2] == ("bin", "hw"):
        matches.append("hal_services")
    if len(parts) >= 2 and parts[:2] in (("lib", "hw"), ("lib64", "hw")):
        matches.append("hal_libraries")
    if len(parts) >= 2 and parts[:2] == ("etc", "vintf"):
        matches.append("vintf")
    if len(parts) >= 2 and parts[:2] == ("etc", "init"):
        matches.append("init_configs")
    if relative.suffix == ".ko":
        matches.append("kernel_modules")
    if "firmware" in parts or parts[:2] == ("etc", "firmware"):
        matches.append("firmware")
    if len(parts) >= 2 and parts[:2] == ("etc", "permissions"):
        matches.append("permissions")
    return tuple(matches)


def inventory(root: Path) -> dict:
    if not root.is_dir():
        raise FileNotFoundError(f"extracted firmware directory is missing: {root}")

    result = {
        "purpose": "Research candidates only; not a complete proprietary extraction list",
        "source": "XT2409-1 RETEU W1UIS36H.39-25-8",
        "partitions": {},
        "candidates": {name: [] for name in CATEGORIES},
    }
    for partition in PARTITIONS:
        partition_root = root / partition
        if not partition_root.is_dir():
            raise FileNotFoundError(f"extracted partition is missing: {partition_root}")
        regular_files = 0
        symlinks = 0
        regular_bytes = 0
        for path in sorted(partition_root.rglob("*")):
            if path.is_symlink():
                symlinks += 1
                continue
            if not path.is_file():
                continue
            regular_files += 1
            regular_bytes += path.stat().st_size
            relative = path.relative_to(partition_root)
            image_path = f"/{partition}/{relative.as_posix()}"
            for category in categories_for(relative):
                result["candidates"][category].append(image_path)
        result["partitions"][partition] = {
            "regular_files": regular_files,
            "symlinks": symlinks,
            "regular_bytes": regular_bytes,
        }
    return result


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=project_root / "stock-firmware/files")
    parser.add_argument("--output", type=Path, default=project_root / "research/firmware-inventory.json")
    args = parser.parse_args()
    data = inventory(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    for category, paths in data["candidates"].items():
        print(f"{category}: {len(paths)}")


if __name__ == "__main__":
    main()
