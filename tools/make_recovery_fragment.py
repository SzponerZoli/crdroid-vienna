#!/usr/bin/env python3
"""Build the vienna Lineage recovery ramdisk fragment from stock vendor_boot.

The phone has no recovery partition: recovery is the second vendor ramdisk
(fragment) of vendor_boot, overlaid on the normal vendor ramdisk. This keeps
Motorola's stock fragment, init, adbd, SELinux policy and libraries, and adds:

- system/bin/recovery.real: the crDroid/Lineage recovery binary;
- system/lib64/vienna-recovery/: its non-bionic library closure from the same
  build (stock copies of e.g. libbase/libfs_mgr are ABI-incompatible);
- system/bin/recovery: a static wrapper (recovery-artifacts/working/rwrap.c)
  that execs recovery.real. init's domain transition sets AT_SECURE, so
  LD_LIBRARY_PATH only works for a second exec inside the recovery domain;
- system/etc/init/hw/init.rc: stock, plus LD_LIBRARY_PATH for the recovery
  service and ADB enabled at boot;
- system/etc/security/otacerts.zip: the build's OTA certificates, so the
  recovery accepts crDroid packages (Motorola's only trusts Motorola OTAs);
- res/: Lineage recovery UI resources.

The result is an lz4-legacy compressed newc cpio for
tools/assemble_recovery_vendorboot.py --fragment.
"""

import argparse
import pathlib
import subprocess
import sys
import tempfile

WORKSPACE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE / "recovery-artifacts/working"))
UNPACK = WORKSPACE / "crdroid/system/tools/mkbootimg/unpack_bootimg.py"
RWRAP = WORKSPACE / "recovery-artifacts/working/rwrap.c"
LIB_DIR = "system/lib64/vienna-recovery"
BIONIC = {"libc.so", "libm.so", "libdl.so", "ld-android.so"}
INIT_LIBPATH = (
    "    # Lineage recovery loads its own crDroid libraries; see /system/bin/recovery wrapper.\n"
    f"    setenv LD_LIBRARY_PATH /{LIB_DIR}\n"
)
INIT_ADB = (
    "\n# vienna: enable ADB in recovery so `adb reboot` and sideload work.\n"
    "on boot\n"
    "    setprop sys.usb.config adb\n"
)


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def needed(path):
    out = subprocess.run(
        ["readelf", "-d", str(path)], check=True, capture_output=True, text=True
    ).stdout
    return [line.split("[", 1)[1].split("]", 1)[0] for line in out.splitlines() if "(NEEDED)" in line]


def library_closure(root, binary):
    search = [root / "system/lib64", root / "system/lib64/hw"]
    found, queue = {}, needed(binary) + ["librecovery_ui_ext.so"]
    while queue:
        name = queue.pop()
        if name in found or name in BIONIC:
            continue
        path = next((d / name for d in search if (d / name).is_file()), None)
        if path is None:
            raise FileNotFoundError(f"{name} not found in recovery build output")
        found[name] = path
        queue.extend(needed(path))
    return found


def patch_init_rc(text):
    header = "service recovery /system/bin/recovery\n"
    service = text.find(header)
    if service < 0:
        raise ValueError("stock init.rc has no recovery service")
    at = service + len(header)
    return text[:at] + INIT_LIBPATH + text[at:] + INIT_ADB


def compile_wrapper(clang, out):
    run(
        clang, "--target=aarch64-linux-android", "-O2", "-ffreestanding", "-nostdlib",
        "-static", "-fno-stack-protector", "-fno-pic", "-Wl,--build-id=none",
        "-o", str(out), str(RWRAP),
    )


def scale_font(src, dst, scale):
    """Scale the recovery font strip (96 glyphs x 2 rows) by an integer factor."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("--font-scale needs Pillow: pip install pillow (or use --font-scale 1)")

    with Image.open(src) as font:
        font.resize((font.width * scale, font.height * scale), Image.NEAREST).save(dst)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stock-vendor-boot", type=pathlib.Path, required=True)
    parser.add_argument("--recovery-root", type=pathlib.Path, required=True,
                        help="out-recovery/target/product/vienna/recovery/root")
    parser.add_argument("--clang", required=True, help="clang from crdroid/prebuilts/clang")
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--font-scale", type=int, default=1,
                        help="enlarge the UI/log font by this integer factor (18x32 -> 36x64 at 2)")
    args = parser.parse_args()
    import cpio_add  # noqa: E402  (recovery-artifacts/working/cpio_add.py)

    root = args.recovery_root.resolve(strict=True)
    binary = root / "system/bin/recovery"
    otacerts = root / "system/etc/security/otacerts.zip"
    for required in (binary, otacerts):
        if not required.is_file():
            raise FileNotFoundError(f"{required.relative_to(root)} not found in recovery build output")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        run(sys.executable, str(UNPACK), "--boot_img", str(args.stock_vendor_boot),
            "--out", str(tmp / "vb"), stdout=subprocess.DEVNULL)
        base = tmp / "fragment.cpio"
        base.write_bytes(run("lz4", "-dc", str(tmp / "vb/vendor_ramdisk01"), capture_output=True).stdout)
        normal = tmp / "normal"
        normal.mkdir()
        run("sh", "-c", f"lz4 -dc '{tmp / 'vb/vendor_ramdisk00'}' | cpio -idm --quiet system/etc/init/hw/init.rc",
            cwd=normal)
        init_rc = tmp / "init.rc"
        init_rc.write_text(patch_init_rc((normal / "system/etc/init/hw/init.rc").read_text()))
        wrapper = tmp / "rwrap"
        compile_wrapper(args.clang, wrapper)

        specs = [f"F:system/bin/recovery:{wrapper}:755",
                 f"F:system/bin/recovery.real:{binary}:755",
                 f"F:system/etc/init/hw/init.rc:{init_rc}:644",
                 # Trust the crDroid build's OTA keys (zip and A/B payload
                 # signatures) instead of Motorola's, so crDroid packages install.
                 f"F:system/etc/security/otacerts.zip:{otacerts}:644",
                 f"D:{LIB_DIR}:755"]
        for name, path in sorted(library_closure(root, binary).items()):
            specs.append(f"F:{LIB_DIR}/{name}:{path}:644")
        # Directory entries must precede their files in the archive.
        specs.append("D:res:755")
        for path in sorted((root / "res").rglob("*")):
            rel = path.relative_to(root).as_posix()
            if rel == "res/images/font.png" and args.font_scale > 1:
                scaled = tmp / "font.png"
                scale_font(path, scaled, args.font_scale)
                path = scaled
            specs.append(f"D:{rel}:755" if path.is_dir() else f"F:{rel}:{path}:644")
        out_cpio = tmp / "out.cpio"
        cpio_add.build(str(base), str(out_cpio), specs)
        run("lz4", "-l", "-12", "-f", str(out_cpio), str(args.out.resolve()), stdout=subprocess.DEVNULL)
    print(f"Wrote {args.out} ({len(specs)} entries added or replaced)")


if __name__ == "__main__":
    main()
