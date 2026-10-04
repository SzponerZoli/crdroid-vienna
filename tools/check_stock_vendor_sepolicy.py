#!/usr/bin/env python3
"""Compile built crDroid policy with the exact stock vendor CIL as init would."""

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "crdroid"
OUT = SOURCE / "out/target/product/vienna"
STOCK = ROOT / "stock-firmware/files/vendor/etc/selinux"
REPORT = ROOT / "research/sepolicy-stock-vendor-compat.json"


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    version = (STOCK / "plat_sepolicy_vers.txt").read_text().strip()
    genfs_version_file = STOCK / "genfs_labels_version.txt"
    genfs_version = genfs_version_file.read_text().strip() if genfs_version_file.exists() else "202404"
    generated = SOURCE / "out/soong/.intermediates/system/sepolicy"
    inputs = [
        generated / "plat_sepolicy.cil/android_common/plat_sepolicy.cil",
        OUT / f"system/etc/selinux/mapping/{version}.cil",
    ]
    platform_compat = SOURCE / f"system/sepolicy/private/compat/{version}/{version}.compat.cil"
    if platform_compat.exists():
        inputs.append(platform_compat)
    inputs.extend(
        [
            generated / "system_ext_sepolicy.cil/android_common/vienna/system_ext_sepolicy.cil",
            OUT / f"system_ext/etc/selinux/mapping/{version}.cil",
            generated / "product_sepolicy.cil/android_common/vienna/product_sepolicy.cil",
            OUT / f"product/etc/selinux/mapping/{version}.cil",
            STOCK / "plat_pub_versioned.cil",
            STOCK / "vendor_sepolicy.cil",
        ]
    )
    genfs = OUT / f"system/etc/selinux/plat_sepolicy_genfs_{genfs_version}.cil"
    if genfs.exists():
        inputs.append(genfs)

    missing = [relative(path) for path in inputs if not path.is_file()]
    report = {
        "purpose": "Host diagnostic mirroring init's split-policy secilc inputs for stock vendor version",
        "stock_vendor_version": version,
        "stock_genfs_labels_version": genfs_version,
        "inputs": [relative(path) for path in inputs],
        "missing_inputs": missing,
    }
    if missing:
        report["result"] = "missing inputs"
        REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 2

    report["input_sha256"] = {
        relative(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs
    }

    with tempfile.TemporaryDirectory(prefix="vienna-policy-") as temp:
        command = [
            str(SOURCE / "out/host/linux-x86/bin/secilc"),
            str(inputs[0]),
            "-m", "-M", "true", "-G", "-N", "-c", "30",
            str(inputs[1]),
            "-o", str(Path(temp) / "policy"),
            "-f", "/dev/null",
            *map(str, inputs[2:]),
        ]
        result = subprocess.run(command, text=True, capture_output=True, check=False)

    report["exit_code"] = result.returncode
    report["result"] = "compiled" if result.returncode == 0 else "failed"
    report["stdout"] = result.stdout
    report["stderr"] = result.stderr
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
