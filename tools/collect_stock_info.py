#!/usr/bin/env python3
"""Collect read-only Edge 50 Neo bring-up facts through ADB."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
import subprocess
import sys


PROPERTY_KEYS = (
    "ro.product.model",
    "ro.product.device",
    "ro.product.vendor.device",
    "ro.product.name",
    "ro.product.system.name",
    "ro.hardware",
    "ro.board.platform",
    "ro.soc.model",
    "ro.build.version.release",
    "ro.build.version.sdk",
    "ro.build.fingerprint",
    "ro.build.id",
    "ro.vendor.build.fingerprint",
    "ro.bootimage.build.fingerprint",
    "ro.build.version.security_patch",
    "ro.vendor.build.security_patch",
    "ro.bootimage.build.version.security_patch",
    "ro.product.first_api_level",
    "ro.board.first_api_level",
    "ro.vndk.version",
    "ro.boot.slot_suffix",
    "ro.boot.hardware.sku",
    "ro.boot.product.hardware.sku",
    "ro.boot.carrier",
    "ro.carrier",
    "ro.boot.cid",
    "ro.boot.flash.locked",
    "ro.boot.verifiedbootstate",
    "ro.virtual_ab.enabled",
    "ro.virtual_ab.compression.enabled",
)

STOCK_FILES = (
    "/vendor/etc/fstab.mt6878",
    "/vendor/etc/fstab.emmc",
    "/vendor/etc/vintf/manifest.xml",
    "/vendor/etc/vintf/compatibility_matrix.xml",
    "/system/etc/vintf/manifest.xml",
)


def adb(*args: str, serial: str | None = None) -> subprocess.CompletedProcess[bytes]:
    command = ["adb"]
    if serial:
        command += ["-s", serial]
    command += list(args)
    return subprocess.run(command, capture_output=True, timeout=30, check=False)


def decoded(data: bytes) -> str:
    return data.decode("utf-8", errors="replace").replace("\r\n", "\n")


def require_device(requested_serial: str | None) -> str:
    result = adb("devices")
    if result.returncode:
        raise RuntimeError(f"ADB unavailable: {decoded(result.stderr).strip()}")
    devices = []
    for line in decoded(result.stdout).splitlines()[1:]:
        fields = line.split()
        if len(fields) >= 2:
            devices.append((fields[0], fields[1]))
    if requested_serial:
        devices = [item for item in devices if item[0] == requested_serial]
    ready = [serial for serial, state in devices if state == "device"]
    if len(ready) != 1:
        raise RuntimeError(
            "Expected one authorized ADB device; connect the phone and accept its USB debugging prompt."
        )
    return ready[0]


def get_property(key: str, serial: str) -> str:
    result = adb("shell", "getprop", key, serial=serial)
    if result.returncode:
        raise RuntimeError(f"Could not read {key}: {decoded(result.stderr).strip()}")
    return decoded(result.stdout).strip()


def collect_file(remote: str, output: Path, serial: str, notes: list[str]) -> None:
    result = adb("exec-out", "cat", remote, serial=serial)
    if result.returncode or not result.stdout:
        notes.append(f"Unavailable: {remote}")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", help="ADB serial if multiple devices are connected")
    parser.add_argument("--output", type=Path, default=Path("stock-info"))
    args = parser.parse_args()

    try:
        serial = require_device(args.serial)
        model = get_property("ro.product.model", serial)
        codename = get_property("ro.product.device", serial)
        if model.casefold() != "motorola edge 50 neo" or codename != "vienna":
            raise RuntimeError(
                f"Connected device is {model!r} ({codename!r}), not an Edge 50 Neo (vienna)."
            )

        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S-UTC")
        output = args.output / f"vienna-{stamp}"
        output.mkdir(parents=True, exist_ok=False)
        notes: list[str] = []

        properties = {key: get_property(key, serial) for key in PROPERTY_KEYS}
        (output / "properties.txt").write_text(
            "".join(f"{key}={value}\n" for key, value in properties.items()),
            encoding="utf-8",
        )

        kernel = adb("shell", "uname", "-r", serial=serial)
        if kernel.returncode == 0:
            (output / "kernel-version.txt").write_text(decoded(kernel.stdout), encoding="utf-8")
        else:
            notes.append("Unavailable: kernel version")

        partitions = adb("shell", "ls", "-l", "/dev/block/by-name", serial=serial)
        if partitions.returncode == 0:
            (output / "partitions.txt").write_text(
                decoded(partitions.stdout), encoding="utf-8"
            )
        else:
            notes.append("Unavailable: /dev/block/by-name listing")

        for remote in STOCK_FILES:
            collect_file(remote, output / remote.lstrip("/"), serial, notes)
        (output / "collection-notes.txt").write_text(
            "\n".join(notes) + ("\n" if notes else ""), encoding="utf-8"
        )
        print(f"Saved read-only stock report to {output}")
        print(f"Model: {model}; build: {properties['ro.build.version.release']}")
        return 0
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
