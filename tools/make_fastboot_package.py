#!/usr/bin/env python3
"""Assemble the crDroid vienna fastboot package (zip of images + flash scripts).

The images must form one verified set: the root vbmeta has to carry the
product and vendor_boot digests of the product.img and vendor_boot.img that
are packaged, and vbmeta_system has to match system and system_ext. This tool
checks that with avbtool before writing the zip.
"""

import argparse
import hashlib
import importlib.util
import pathlib
import zipfile

WORKSPACE = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = WORKSPACE / "tools/fastboot-package"
AVBTOOL = WORKSPACE / "crdroid/external/avb/avbtool.py"
IMAGES = ("vbmeta", "vendor_boot", "system", "system_ext", "product", "vbmeta_system")


def load_avbtool():
    spec = importlib.util.spec_from_file_location("vienna_avbtool", AVBTOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def descriptors(avbtool, path):
    image = avbtool.ImageHandler(str(path), read_only=True)
    return avbtool.Avb()._parse_image(image)[2]


def by_partition(avbtool, descs, name):
    for d in descs:
        if isinstance(d, (avbtool.AvbHashDescriptor, avbtool.AvbHashtreeDescriptor)) \
                and d.partition_name == name:
            return d
    raise ValueError(f"no descriptor for {name}")


def check_set(images):
    avbtool = load_avbtool()
    root = descriptors(avbtool, images["vbmeta"])
    for name in ("product", "vendor_boot"):
        want = by_partition(avbtool, root, name)
        have = by_partition(avbtool, descriptors(avbtool, images[name]), name)
        field = "root_digest" if name == "product" else "digest"
        if getattr(want, field) != getattr(have, field):
            raise ValueError(f"root vbmeta does not match {images[name]}")
    chain = descriptors(avbtool, images["vbmeta_system"])
    for name in ("system", "system_ext"):
        want = by_partition(avbtool, chain, name)
        have = by_partition(avbtool, descriptors(avbtool, images[name]), name)
        if want.root_digest != have.root_digest:
            raise ValueError(f"vbmeta_system does not match {images[name]}")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in IMAGES:
        parser.add_argument(f"--{name.replace('_', '-')}", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    images = {name: getattr(args, name).resolve(strict=True) for name in IMAGES}
    if args.out.exists():
        parser.error(f"output already exists: {args.out}")

    check_set(images)
    stem = args.out.name.removesuffix(".zip")
    sums = "".join(f"{sha256(p)}  images/{n}.img\n" for n, p in images.items())
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, path in images.items():
            z.write(path, f"{stem}/images/{name}.img")
        z.writestr(f"{stem}/SHA256SUMS", sums)
        for script in ("flash.sh", "flash.bat", "README.txt"):
            info = zipfile.ZipInfo.from_file(TEMPLATE / script, f"{stem}/{script}")
            info.compress_type = zipfile.ZIP_DEFLATED
            if script == "flash.sh":
                info.external_attr = 0o100755 << 16
            z.writestr(info, (TEMPLATE / script).read_bytes())
    print(f"Wrote {args.out}")
    print(sums, end="")


if __name__ == "__main__":
    main()
