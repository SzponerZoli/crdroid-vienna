#!/usr/bin/env python3
"""Inventory stock init services that execute files from system_ext.

This reports extraction coverage, not whether an AOSP source module provides
the same service in the eventual image.
"""

import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STOCK = ROOT / "stock-firmware/files"
PROPRIETARY_LIST = ROOT / "device/motorola/vienna/proprietary-files.txt"
OUTPUT = ROOT / "research/system-ext-services.json"


def listed_paths() -> set[str]:
    result = set()
    for line in PROPRIETARY_LIST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            result.add(line.split(";", 1)[0].split(":", 1)[0])
    return result


def stock_relative_path(path: str) -> str | None:
    if path.startswith("/system_ext/"):
        return path.removeprefix("/")
    if path.startswith("/system/system_ext/"):
        return path.removeprefix("/system/")
    return None


def needed_libraries(executable: Path) -> list[str]:
    if not executable.is_file():
        return []
    result = subprocess.run(
        ["readelf", "-d", str(executable)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return sorted(set(re.findall(r"\(NEEDED\).*?\[([^]]+)\]", result.stdout)))


def collect_services(selected: set[str]) -> list[dict]:
    services = []
    for partition in ("system_ext", "vendor"):
        init_dir = STOCK / partition / "etc/init"
        for rc in sorted(init_dir.rglob("*.rc")):
            rc_path = rc.relative_to(STOCK).as_posix()
            for line_number, line in enumerate(
                rc.read_text(encoding="utf-8", errors="replace").splitlines(), 1
            ):
                match = re.match(r"\s*service\s+(\S+)\s+(\S+)", line)
                if not match:
                    continue
                executable = stock_relative_path(match.group(2))
                if executable is None:
                    continue
                services.append(
                    {
                        "service": match.group(1),
                        "executable": executable,
                        "stock_executable_exists": (STOCK / executable).is_file(),
                        "needed_libraries": needed_libraries(STOCK / executable),
                        "executable_in_proprietary_list": executable in selected,
                        "init_file": rc_path,
                        "init_file_in_proprietary_list": rc_path in selected,
                        "line": line_number,
                    }
                )
    return sorted(services, key=lambda item: (item["service"], item["init_file"]))


def collect_vintf_fragments(selected: set[str]) -> list[dict]:
    fragments = []
    directory = STOCK / "system_ext/etc/vintf/manifest"
    for fragment in sorted(directory.glob("*.xml")):
        path = fragment.relative_to(STOCK).as_posix()
        root = ET.parse(fragment).getroot()
        fragments.append(
            {
                "file": path,
                "hal_names": sorted(
                    name.text
                    for name in root.findall("./hal/name")
                    if name.text is not None
                ),
                "in_proprietary_list": path in selected,
            }
        )
    return fragments


def main() -> None:
    selected = listed_paths()
    report = {
        "method": "Stock init service and VINTF fragment inventory; extraction coverage only",
        "services": collect_services(selected),
        "system_ext_vintf_fragments": collect_vintf_fragments(selected),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    services = report["services"]
    missing = sum(
        service["stock_executable_exists"]
        and not service["executable_in_proprietary_list"]
        for service in services
    )
    print(
        f"{len(services)} stock service declarations, "
        f"{missing} stock binaries outside the current list"
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
