#!/usr/bin/env python3
"""Refresh the product hashtree descriptor in an existing root vbmeta.

The root vbmeta carries the product partition's hashtree digest. Flashing a
rebuilt product.img without refreshing it makes first-stage init hang. This
copies the new product hashtree descriptor and product build properties from
the built product.img footer into the given root vbmeta and re-signs it with
the same test key, rollback index, and flags. All other descriptors (boot,
vendor_boot, vbmeta_system chain, Motorola properties) stay untouched.
"""

import argparse
import pathlib

from make_matching_recovery_vbmeta import load_avbtool, parse, TEST_KEY


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=pathlib.Path, help="current root vbmeta")
    parser.add_argument("--product", required=True, type=pathlib.Path, help="built product.img")
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()
    if args.out.exists():
        parser.error(f"output already exists: {args.out}")

    avb = load_avbtool()
    _, header, descriptors, _ = parse(avb, args.root)
    _, _, product_descriptors, _ = parse(avb, args.product)
    new_tree = [d for d in product_descriptors
                if isinstance(d, avb.AvbHashtreeDescriptor) and d.partition_name == "product"]
    slots = [i for i, d in enumerate(descriptors)
             if isinstance(d, avb.AvbHashtreeDescriptor) and d.partition_name == "product"]
    if len(new_tree) != 1 or len(slots) != 1:
        raise ValueError("expected exactly one product hashtree descriptor in each input")
    new_props = {d.key: d.value for d in product_descriptors
                 if isinstance(d, avb.AvbPropertyDescriptor)}

    original = [d.encode() for d in descriptors]
    descriptors[slots[0]] = new_tree[0]
    for d in descriptors:
        if isinstance(d, avb.AvbPropertyDescriptor) and d.key.startswith("com.android.build.product."):
            d.value = new_props[d.key]

    blob = avb.Avb()._generate_vbmeta_blob(
        algorithm_name="SHA256_RSA2048", key_path=str(TEST_KEY), public_key_metadata_path=None,
        descriptors=descriptors, chain_partitions_use_ab=None, chain_partitions_do_not_use_ab=None,
        rollback_index=header.rollback_index, flags=header.flags,
        rollback_index_location=header.rollback_index_location, props=None, props_from_file=None,
        kernel_cmdlines=None, setup_rootfs_from_kernel=None, ht_desc_to_setup=None,
        include_descriptors_from_image=None, signing_helper=None, signing_helper_with_files=None,
        release_string=header.release_string, append_to_release_string=None,
        required_libavb_version_minor=header.required_libavb_version_minor)
    size = args.root.stat().st_size
    if len(blob) > size:
        raise ValueError("signed vbmeta exceeds the original image size")
    args.out.write_bytes(blob.ljust(size, b"\0"))

    _, out_header, out_descriptors, _ = parse(avb, args.out)
    changed = [i for i, (a, b) in enumerate(zip(original, out_descriptors)) if a != b.encode()]
    if (len(out_descriptors) != len(original) or out_header.rollback_index != header.rollback_index
            or out_header.flags != header.flags or any(
                not isinstance(out_descriptors[i], (avb.AvbHashtreeDescriptor, avb.AvbPropertyDescriptor))
                for i in changed)):
        args.out.unlink()
        raise ValueError("generated vbmeta changed unexpected fields")
    print(f"Wrote {args.out}; changed descriptor indices: {changed}")


if __name__ == "__main__":
    main()
