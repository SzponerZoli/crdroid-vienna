# Fastbootd installation assessment for XT2409-1

Checked 2026-10-01 against the connected unlocked XT2409-1 running Motorola
`W1UIS36H.39-25-8`. This is an assessment, not an install procedure. No ROM
partition was flashed during these checks.

## Device capability

`adb reboot fastboot` entered Motorola's stock userspace fastboot. Read-only
queries returned `is-userspace: yes`, `current-slot: a`,
`is-logical:system_a: yes`, and `partition-size:super: 0x560000000`
(23,085,449,216 bytes). `fastboot reboot` returned to Android; ADB reported
`sys.boot_completed=1`. [AOSP fastbootd documentation](https://source.android.com/docs/core/architecture/bootloader/fastbootd)
describes userspace fastboot as the mode that can manage logical partitions.

The phone's `lpdump` reports virtual A/B metadata version 10.2 and no pending
snapshot update. Its logical partitions are in `main_a` and `main_b` groups,
each with maximum size 23,083,352,064 bytes. The exact-model firmware's
`super` metadata matches these values. The existing prototype target-files
package instead describes `motorola_dynamic_partitions_a` and
`motorola_dynamic_partitions_b` groups, with a slightly smaller maximum size.
The device tree now specifies the stock group names and size. An interrupted
2026-10-01 target-files rebuild produced an intermediate `super_empty.img`
with `main_a` and `main_b`, each at the phone's exact group maximum. The
target-files ZIP was left at 0 bytes and must be rebuilt before use.

## Package findings

The prototype target-files `META/fastboot-info.txt` flashes `boot`,
`init_boot`, `dtbo`, `vendor_boot`, `vbmeta`, `vbmeta_system`, then enters
fastbootd to update `super` and flash its logical partitions. The unpadded
boot, init_boot, DTBO, and vendor_boot payload bytes match exact-model stock,
although the generated images have different AVB footers and full-file hashes.

The prototype root `vbmeta` uses Android's development test key, has rollback
index **0**, and lacks stock Motorola `KERN_PROT_META` and `HAB_META`
properties. Stock root `vbmeta` uses rollback index **25** and contains both
properties. The child `vbmeta_system` already uses rollback index 25 but also
lacks those two Motorola properties. The device tree now specifies rollback
level 25 and both properties for root and child metadata. The interrupted
rebuild's intermediate `vbmeta.img` and `vbmeta_system.img` were inspected:
both have rollback index 25 and both Motorola properties. The ZIP packaging
did not finish, so these intermediates do not make a usable install package.

`tools/make_stockboot_crdroid_vbmeta.py` generated an experimental root
`vbmeta` preserving stock boot/vendor descriptors while using the built
product descriptor and test-key `vbmeta_system` chain. A strict host
`avbtool verify_image --follow_chain_partitions` check passed for this root,
the built system, system_ext, product images, and exact stock boot/vendor
images. See [the artifact note](../install-artifacts/README.md). This does not
establish that the phone can boot crDroid.

No boot test of the crDroid system images has occurred. The OTA ZIP is signed
with a development key and remains an unbooted candidate. A fastbootd route
still needs a regenerated package, package-level validation, a backup
and rollback plan for shared `/data`, and a controlled first boot test.
