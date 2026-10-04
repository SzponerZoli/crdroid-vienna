#!/usr/bin/env python3
"""List stock vendor references to stock system_ext SELinux types."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STOCK = ROOT / "stock-firmware/files"
SOURCE = ROOT / "crdroid/device/mediatek/sepolicy_vndr/base"


def main() -> None:
    stock_system_ext = (
        STOCK / "system_ext/etc/selinux/system_ext_sepolicy.cil"
    ).read_text(encoding="utf-8")
    stock_vendor = (STOCK / "vendor/etc/selinux/vendor_sepolicy.cil").read_text(
        encoding="utf-8"
    )

    system_ext_types = set(re.findall(r"\(type ([^ ()]+)\)", stock_system_ext))
    vendor_tokens = set(re.findall(r"[A-Za-z0-9_.-]+", stock_vendor))
    referenced = {
        name
        for name in system_ext_types
        if name in vendor_tokens or f"{name}_34_0" in vendor_tokens
    }

    generic_source = "\n".join(
        path.read_text(encoding="utf-8")
        for area in (SOURCE / "public", SOURCE / "private")
        for path in area.rglob("*.te")
    )
    generic_types = set(
        re.findall(r"\btype\s+([A-Za-z0-9_]+)\s*[,;]", generic_source)
    )

    report = {
        "method": "Static name scan of stock CIL and generic MediaTek .te declarations; not a policy compiler result",
        "stock_system_ext_type_count": len(system_ext_types),
        "vendor_referenced_system_ext_types": sorted(referenced),
        "declared_in_generic_mediatek_source": sorted(referenced & generic_types),
        "not_declared_in_generic_mediatek_source": sorted(referenced - generic_types),
    }
    destination = ROOT / "research/sepolicy-crossrefs.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"{len(referenced)} stock system_ext types referenced by vendor CIL; "
        f"{len(referenced - generic_types)} absent from generic MediaTek .te declarations"
    )
    print(destination)


if __name__ == "__main__":
    main()
