#!/usr/bin/env python3
"""Build a stock-based recovery ramdisk with the Lineage recovery program.

Keeps Motorola's recovery init, fstab, SELinux policy and normal vendor ramdisk.
The output is a host artifact; this script does not write to a phone.
"""

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile


WORKSPACE = pathlib.Path(__file__).resolve().parent.parent
STOCK_ROOT = WORKSPACE / "stock-firmware/recovery-work/stock25-recovery-root"
STOCK_NORMAL_ROOT = WORKSPACE / "stock-firmware/recovery-work/stock25-normal-root"
BUILT_ROOT = WORKSPACE / "crdroid/out-recovery/target/product/vienna/recovery/root"

BUILT_FILES = (
    "system/bin/recovery",
    "system/lib64/android.hardware.health-V4-ndk.so",
    "system/lib64/libvolume_manager.so",
    "system/lib64/librecovery_ui.so",
    "system/lib64/librecovery_ui_ext.so",
    "system/lib64/libsgdisk.so",
    "system/lib64/libsysutils.so",
    "system/lib64/libc++.so",
    "system/lib64/libbinder_ndk.so",
    "system/lib64/libbinder.so",
)


def check_recovery_abi(root):
    """Check the recovery ELF dependency closure against the combined ramdisks."""
    libraries = {
        path.name: path for path in (STOCK_NORMAL_ROOT / "system/lib64").glob("*.so")
    }
    libraries.update({
        path.name: path for path in (root / "system/lib64").glob("*.so")
    })
    pending = [root / "system/bin/recovery"]
    checked = set()
    exports = set()
    imports = {}
    while pending:
        path = pending.pop()
        if path.name in checked:
            continue
        checked.add(path.name)
        dynamic = subprocess.check_output(["readelf", "-d", path], text=True)
        for name in re.findall(r"\(NEEDED\)\s+Shared library: \[(.*?)\]", dynamic):
            if name not in libraries:
                raise RuntimeError(f"{path.name} needs absent library {name}")
            pending.append(libraries[name])
        symbols = subprocess.check_output(
            ["nm", "-D", "--format=posix", path], text=True
        )
        for line in symbols.splitlines():
            fields = line.split()
            if len(fields) < 2:
                continue
            symbol = fields[0].replace("@@", "@")
            if fields[1] == "U":
                imports.setdefault(symbol, set()).add(path.name)
            else:
                exports.add(symbol)
    export_names = {name.split("@")[0] for name in exports}
    missing = {
        symbol: users for symbol, users in imports.items()
        if symbol not in exports and ("@" in symbol or symbol not in export_names)
    }
    if missing:
        sample = ", ".join(sorted(missing)[:5])
        raise RuntimeError(f"recovery has {len(missing)} unresolved ELF symbols: {sample}")
    print(f"Recovery ELF ABI check passed ({len(checked)} libraries and program)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()
    output = args.out.resolve()
    if output.exists():
        parser.error(f"output already exists: {output}")
    if not STOCK_ROOT.is_dir() or not STOCK_NORMAL_ROOT.is_dir() or not BUILT_ROOT.is_dir():
        parser.error("stock or built recovery root is missing")

    with tempfile.TemporaryDirectory(prefix="vienna-recovery-overlay-") as temp_name:
        root = pathlib.Path(temp_name) / "root"
        shutil.copytree(STOCK_ROOT, root, symlinks=True)
        for relative in BUILT_FILES:
            source = BUILT_ROOT / relative
            if not source.is_file():
                parser.error(f"built file is missing: {source}")
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        shutil.copytree(BUILT_ROOT / "res", root / "res", dirs_exist_ok=True)
        check_recovery_abi(root)

        paths = [b"."] + sorted(
            str(path.relative_to(root)).encode()
            for path in root.rglob("*")
        )
        file_list = b"\0".join(paths) + b"\0"
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("wb") as destination:
            cpio = subprocess.Popen(
                ["cpio", "-o", "-0", "-H", "newc", "-R", "0:0"],
                cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            compressor = subprocess.Popen(
                ["lz4", "-l", "-z", "-c"],
                stdin=cpio.stdout, stdout=destination, stderr=subprocess.PIPE,
            )
            cpio.stdout.close()
            _, cpio_errors = cpio.communicate(file_list)
            _, lz4_errors = compressor.communicate()
        if cpio.returncode or compressor.returncode:
            output.unlink(missing_ok=True)
            raise RuntimeError(
                f"ramdisk packaging failed: cpio={cpio.returncode} {cpio_errors.decode()} "
                f"lz4={compressor.returncode} {lz4_errors.decode()}"
            )
        print(f"Stock-based recovery fragment: {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
