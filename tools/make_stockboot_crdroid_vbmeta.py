#!/usr/bin/env python3
"""Prepare root AVB metadata for a stock-boot, crDroid-system fastboot test.

This host-only tool preserves Motorola's exact boot/vendor descriptors and
properties. It substitutes the built product descriptor, product properties,
and test-key vbmeta_system chain key, then signs with the Android test key.
It does not flash a device or make the ROM bootable by itself.
"""

import argparse
import pathlib
import sys

from make_matching_recovery_vbmeta import load_avbtool, parse, TEST_KEY


def unique(descriptors, klass, name):
    matches = [d for d in descriptors if isinstance(d, klass) and d.partition_name == name]
    if len(matches) != 1:
        raise ValueError(f"expected one {name} {klass.__name__}, found {len(matches)}")
    return matches[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-root", required=True, type=pathlib.Path)
    parser.add_argument("--built-root", required=True, type=pathlib.Path)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()
    stock = args.stock_root.resolve(strict=True)
    built = args.built_root.resolve(strict=True)
    output = args.out.resolve()
    if output.exists():
        parser.error(f"output already exists: {output}")

    avbtool = load_avbtool()
    _, stock_header, stock_descriptors, _ = parse(avbtool, stock)
    _, built_header, built_descriptors, _ = parse(avbtool, built)
    if stock_header.rollback_index != 25 or built_header.rollback_index != 25:
        raise ValueError("root rollback index is not 25 in both inputs")
    if stock_header.flags != 0 or built_header.flags != 0:
        raise ValueError("unexpected AVB verification flags")
    stock_chain = unique(stock_descriptors, avbtool.AvbChainPartitionDescriptor, "vbmeta_system")
    built_chain = unique(built_descriptors, avbtool.AvbChainPartitionDescriptor, "vbmeta_system")
    if stock_chain.rollback_index_location != 2 or built_chain.rollback_index_location != 2:
        raise ValueError("vbmeta_system chain uses an unexpected rollback location")
    stock_product = unique(stock_descriptors, avbtool.AvbHashtreeDescriptor, "product")
    built_product = unique(built_descriptors, avbtool.AvbHashtreeDescriptor, "product")

    original = [d.encode() for d in stock_descriptors]
    stock_chain.public_key = built_chain.public_key
    stock_descriptors[stock_descriptors.index(stock_product)] = built_product
    built_properties = {
        d.key: d.value for d in built_descriptors
        if isinstance(d, avbtool.AvbPropertyDescriptor)
        and d.key.startswith("com.android.build.product.")
    }
    stock_properties = {
        d.key: d for d in stock_descriptors
        if isinstance(d, avbtool.AvbPropertyDescriptor)
        and d.key.startswith("com.android.build.product.")
    }
    if set(stock_properties) != set(built_properties):
        raise ValueError("built and stock product AVB property keys differ")
    for key, descriptor in stock_properties.items():
        descriptor.value = built_properties[key]

    blob = avbtool.Avb()._generate_vbmeta_blob(
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
    if len(blob) > stock.stat().st_size:
        raise ValueError("signed vbmeta exceeds the stock image size")
    image = blob.ljust(stock.stat().st_size, b"\0")
    header = avbtool.AvbVBMetaHeader(image[:avbtool.AvbVBMetaHeader.SIZE])
    if not avbtool.verify_vbmeta_signature(header, image):
        raise ValueError("generated vbmeta signature is invalid")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(image)
    _, result_header, result_descriptors, _ = parse(avbtool, output)
    differences = [
        index for index, (before, after) in enumerate(zip(original, result_descriptors))
        if before != after.encode()
    ]
    expected = [
        index for index, (before, after) in enumerate(zip(original, stock_descriptors))
        if before != after.encode()
    ]
    if len(result_descriptors) != len(original) or differences != expected:
        output.unlink(missing_ok=True)
        raise ValueError("generated vbmeta changed unexpected descriptors")
    if result_header.rollback_index != 25 or result_header.flags != 0:
        output.unlink(missing_ok=True)
        raise ValueError("generated vbmeta changed rollback or verification flags")
    print(f"Host-signed stock-boot crDroid vbmeta: {output} ({len(image)} bytes)")
    print(f"Changed descriptor indices: {differences}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
