#!/usr/bin/env python3
"""Combine a built recovery ramdisk with the exact-model stock vendor_boot.

This is a host-only operation. It does not connect to or write to a device.
"""

import argparse
import filecmp
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile


WORKSPACE = pathlib.Path(__file__).resolve().parent.parent
TOOLS = WORKSPACE / "crdroid/out/host/linux-x86/bin"
PARTITION_SIZE = 67_108_864


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def unpack(image, directory):
    output = run(
        TOOLS / "unpack_bootimg",
        "--boot_img", image,
        "--out", directory,
        "--format=mkbootimg", "-0",
        stdout=subprocess.PIPE,
    ).stdout
    return [arg.decode() for arg in output.rstrip(b"\0").split(b"\0")]


def recovery_fragment(args):
    for index, value in enumerate(args):
        if value == "--ramdisk_name" and args[index + 1] == "recovery":
            try:
                fragment_arg = args.index("--vendor_ramdisk_fragment", index + 2)
            except ValueError as error:
                raise ValueError("recovery fragment has no file") from error
            return fragment_arg + 1
    raise ValueError("image has no named recovery ramdisk fragment")


def check_stock_footer(image):
    info = run(
        TOOLS / "avbtool", "info_image", "--image", image,
        stdout=subprocess.PIPE, text=True,
    ).stdout
    if not re.search(r"^Image size:\s+67108864 bytes$", info, re.MULTILINE):
        raise ValueError("stock vendor_boot is not the expected 64 MiB size")
    if not re.search(r"^Algorithm:\s+NONE$", info, re.MULTILINE):
        raise ValueError("stock vendor_boot footer uses an unexpected AVB algorithm")
    if not re.search(r"^\s+Partition Name:\s+vendor_boot$", info, re.MULTILINE):
        raise ValueError("stock image has no vendor_boot hash descriptor")
    salt = re.search(r"^\s+Salt:\s+([0-9a-f]+)$", info, re.MULTILINE)
    if not salt:
        raise ValueError("stock vendor_boot AVB salt is missing")
    return salt.group(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock", type=pathlib.Path, required=True)
    recovery_input = parser.add_mutually_exclusive_group(required=True)
    recovery_input.add_argument("--built", type=pathlib.Path)
    recovery_input.add_argument("--fragment", type=pathlib.Path)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument(
        "--extra-cmdline",
        default="",
        help="text appended to the stock vendor kernel command line (debugging)",
    )
    args = parser.parse_args()
    stock = args.stock.resolve(strict=True)
    built = args.built.resolve(strict=True) if args.built else None
    fragment = args.fragment.resolve(strict=True) if args.fragment else None
    output = args.out.resolve()
    if output.exists():
        parser.error(f"output already exists: {output}")
    if stock == built:
        parser.error("the built image must differ from stock")
    salt = check_stock_footer(stock)
    with tempfile.TemporaryDirectory(prefix="vienna-recovery-") as temp_name:
        temp = pathlib.Path(temp_name)
        stock_args = unpack(stock, temp / "stock")
        stock_index = recovery_fragment(stock_args)
        if args.extra_cmdline:
            cmdline_index = stock_args.index("--vendor_cmdline") + 1
            stock_args[cmdline_index] = f"{stock_args[cmdline_index]} {args.extra_cmdline}".strip()
        if built:
            built_args = unpack(built, temp / "built")
            built_index = recovery_fragment(built_args)
            built_fragment = pathlib.Path(built_args[built_index])
        else:
            built_fragment = fragment
        if not built_fragment.is_file():
            raise ValueError("built recovery fragment is missing")
        stock_args[stock_index] = str(built_fragment)
        assembled = temp / "vendor_boot.img"
        run(TOOLS / "mkbootimg", *stock_args, "--vendor_boot", assembled)
        raw_size = assembled.stat().st_size
        try:
            if raw_size > PARTITION_SIZE - 4096:
                raise ValueError(
                    f"image does not fit vendor_boot with an AVB footer: {raw_size} bytes"
                )
            run(
                TOOLS / "avbtool", "add_hash_footer",
                "--image", assembled,
                "--partition_size", str(PARTITION_SIZE),
                "--partition_name", "vendor_boot",
                "--salt", salt,
            )
            run(TOOLS / "avbtool", "verify_image", "--image", assembled)
            result_args = unpack(assembled, temp / "result")
            result_index = recovery_fragment(result_args)
            for flag in ("--dtb", "--vendor_bootconfig"):
                stock_value = pathlib.Path(stock_args[stock_args.index(flag) + 1]).read_bytes()
                result_value = pathlib.Path(result_args[result_args.index(flag) + 1]).read_bytes()
                if stock_value != result_value:
                    raise ValueError(f"stock {flag} changed")
            if pathlib.Path(result_args[result_index]).read_bytes() != built_fragment.read_bytes():
                raise ValueError("recovery ramdisk changed during repack")
            stock_normal = pathlib.Path(stock_args[stock_args.index("--vendor_ramdisk_fragment") + 1])
            result_normal = pathlib.Path(result_args[result_args.index("--vendor_ramdisk_fragment") + 1])
            if stock_normal.read_bytes() != result_normal.read_bytes():
                raise ValueError("stock normal vendor ramdisk changed")
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(assembled, output)
            if not filecmp.cmp(assembled, output, shallow=False):
                raise ValueError("output copy differs from validated image")
            print(f"Host-validated vendor_boot: {output} ({output.stat().st_size} bytes)")
            print(f"Unpadded boot image: {raw_size} bytes")
        except Exception:
            output.unlink(missing_ok=True)
            raise


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Recovery assembly failed: {error}", file=sys.stderr)
        sys.exit(1)
