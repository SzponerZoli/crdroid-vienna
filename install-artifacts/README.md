# Experimental install metadata

> The image files described here are **not published**: they are built from
> Motorola stock firmware and contain proprietary content. This file is kept as
> a record of what was built and tested.

`vbmeta-stockboot-crdroid-host-prototype.img` is an 8,192-byte **host-only
prototype**, SHA-256
`8dc6d687d5c6d9e2e72a5beff41887da6ec9e5fd3eba1e36348f146c4ed2bc43`.
It was generated with `tools/make_stockboot_crdroid_vbmeta.py` from exact
XT2409-1 stock root `vbmeta` and the corrected but incompletely packaged
crDroid target-files intermediates from 2026-10-01. It preserves Motorola's
stock boot, DTBO, init_boot, vendor_boot, vendor and module AVB descriptors,
and changes the product descriptor/properties and the `vbmeta_system` chain
key to the Android development test key. Root rollback index remains 25.

A strict host `avbtool verify_image --follow_chain_partitions` check, with the
expected `vbmeta_system` key at rollback location 2, passed against the built
system, system_ext and product images plus exact-model stock images. This is
not a complete fastboot package or a device boot test. **Do not flash it.**
Regenerate and reverify it after a successful target-files rebuild.
