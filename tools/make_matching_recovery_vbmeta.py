#!/usr/bin/env python3
"""Sign stock AVB descriptors with a vendor_boot hash for a recovery test.

This is a host-only operation. It preserves all stock descriptors, properties,
rollback index and flags; only the vendor_boot image size and digest change.
"""

import argparse
import hashlib
import importlib.util
import pathlib
import sys


WORKSPACE = pathlib.Path(__file__).resolve().parent.parent
AVBTOOL = WORKSPACE / "crdroid/external/avb/avbtool.py"
TEST_KEY = WORKSPACE / "crdroid/external/avb/test/data/testkey_rsa2048.pem"


def load_avbtool():
    spec = importlib.util.spec_from_file_location("vienna_avbtool", AVBTOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse(avbtool, path):
    image = avbtool.ImageHandler(str(path), read_only=True)
    return avbtool.Avb()._parse_image(image)


def vendor_boot_descriptor(avbtool, descriptors):
    matches = [
        descriptor for descriptor in descriptors
        if isinstance(descriptor, avbtool.AvbHashDescriptor)
        and descriptor.partition_name == "vendor_boot"
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one vendor_boot descriptor, found {len(matches)}")
    return matches[0]


def image_digest(path, image_size, salt):
    digest = hashlib.sha256()
    digest.update(salt)
    with path.open("rb") as image:
        remaining = image_size
        while remaining:
            chunk = image.read(min(1024 * 1024, remaining))
            if not chunk:
                raise ValueError(f"image is shorter than descriptor: {path}")
            digest.update(chunk)
            remaining -= len(chunk)
    return digest.digest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-vbmeta", type=pathlib.Path, required=True)
    parser.add_argument("--stock-vendor-boot", type=pathlib.Path, required=True)
    parser.add_argument("--recovery-vendor-boot", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    stock_vbmeta = args.stock_vbmeta.resolve(strict=True)
    stock_vendor_boot = args.stock_vendor_boot.resolve(strict=True)
    recovery_vendor_boot = args.recovery_vendor_boot.resolve(strict=True)
    output = args.out.resolve()
    if output.exists():
        parser.error(f"output already exists: {output}")

    avbtool = load_avbtool()
    _, stock_header, stock_descriptors, _ = parse(avbtool, stock_vbmeta)
    _, _, recovery_descriptors, _ = parse(avbtool, recovery_vendor_boot)
    stock_hash = vendor_boot_descriptor(avbtool, stock_descriptors)
    recovery_hash = vendor_boot_descriptor(avbtool, recovery_descriptors)
    if stock_header.flags != 0 or stock_header.rollback_index_location != 0:
        raise ValueError("stock vbmeta has unexpected flags or rollback location")
    if stock_hash.hash_algorithm != "sha256" or stock_hash.salt != recovery_hash.salt:
        raise ValueError("vendor_boot hash algorithm or salt differs from stock")
    if image_digest(stock_vendor_boot, stock_hash.image_size, stock_hash.salt) != stock_hash.digest:
        raise ValueError("stock vendor_boot does not match stock vbmeta")
    if image_digest(recovery_vendor_boot, recovery_hash.image_size, recovery_hash.salt) != recovery_hash.digest:
        raise ValueError("recovery vendor_boot footer hash is invalid")
    original_descriptors = [descriptor.encode() for descriptor in stock_descriptors]
    stock_hash.image_size = recovery_hash.image_size
    stock_hash.digest = recovery_hash.digest

    vbmeta_blob = avbtool.Avb()._generate_vbmeta_blob(
        algorithm_name="SHA256_RSA2048",
        key_path=str(TEST_KEY),
        public_key_metadata_path=None,
        descriptors=stock_descriptors,
        chain_partitions_use_ab=None,
        chain_partitions_do_not_use_ab=None,
        rollback_index=stock_header.rollback_index,
        flags=stock_header.flags,
        rollback_index_location=stock_header.rollback_index_location,
        props=None,
        props_from_file=None,
        kernel_cmdlines=None,
        setup_rootfs_from_kernel=None,
        ht_desc_to_setup=None,
        include_descriptors_from_image=None,
        signing_helper=None,
        signing_helper_with_files=None,
        release_string=stock_header.release_string,
        append_to_release_string=None,
        required_libavb_version_minor=stock_header.required_libavb_version_minor,
    )
    if len(vbmeta_blob) > stock_vbmeta.stat().st_size:
        raise ValueError("signed vbmeta does not fit the stock image size")
    padded = vbmeta_blob.ljust(stock_vbmeta.stat().st_size, b"\0")
    header = avbtool.AvbVBMetaHeader(padded[:avbtool.AvbVBMetaHeader.SIZE])
    if not avbtool.verify_vbmeta_signature(header, padded):
        raise ValueError("generated vbmeta signature is invalid")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(padded)
    _, result_header, result_descriptors, _ = parse(avbtool, output)
    result_bytes = [descriptor.encode() for descriptor in result_descriptors]
    differences = [
        index for index, (before, after) in enumerate(zip(original_descriptors, result_bytes))
        if before != after
    ]
    vendor_index = stock_descriptors.index(stock_hash)
    expected_differences = [vendor_index] if original_descriptors[vendor_index] != stock_hash.encode() else []
    if len(result_bytes) != len(original_descriptors) or differences != expected_differences:
        output.unlink(missing_ok=True)
        raise ValueError("generated vbmeta changed descriptors beyond vendor_boot")
    if result_header.rollback_index != stock_header.rollback_index or result_header.flags != stock_header.flags:
        output.unlink(missing_ok=True)
        raise ValueError("generated vbmeta changed rollback or verification flags")
    print(f"Matching test-key vbmeta: {output} ({len(padded)} bytes)")
    print(f"Vendor_boot hash image size: {recovery_hash.image_size} bytes")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
