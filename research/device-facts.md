# Edge 50 Neo source and partition facts

These facts apply to the attached **XT2409-1 / RETEU** phone and its
**W1UIS36H.39-25-8** stock package. The owner updated the phone to this
exact build on 2026-10-01; ADB confirmed it after the recovery tests.

## Device report

The original read-only ADB report is under
`stock-info/vienna-20260928-162841-UTC/`. It predates the firmware update and
bootloader unlock. The current device reports `vienna`, `mt6878`, Android 16
(SDK 36), launch API 34, slot `_a`, virtual A/B updates, and an unlocked
bootloader. The kernel reports
`6.1.141-android14-11-gd77c4cd65aed-ab14680598`.
Read-only `wm` queries report a 1200 × 2670 physical display at 450 dpi.

## Extracted firmware

The firmware ZIP passed `unzip -tq`. Its 31 `super.img_sparsechunk` files were
assembled with `simg2img`, then the active logical images were extracted with
`lpunpack`. Their EROFS contents are under `stock-firmware/files/`:

| Partition | Source image | Approximate extracted size |
| --- | --- | ---: |
| system | `system_a.img` | 1.1 GiB |
| system_ext | `system_ext_a.img` | 1.1 GiB |
| product | `product_a.img` | 5.8 GiB |
| vendor | `vendor_a.img` | 2.6 GiB |
| system_dlkm | `system_dlkm_a.img` | 11 MiB |
| vendor_dlkm | `vendor_dlkm_a.img` | 46 MiB |

`super` is 23,085,449,216 bytes and has `main_a` and `main_b` dynamic
partition groups. The stock fstab has EROFS and ext4 entries for the logical
partitions; the supplied images are EROFS. `userdata` and `metadata` use F2FS.
`userdata` uses inline encryption with wrapped keys, and its metadata key is
under `/metadata/vold/metadata_encryption`.

The package's primary GPT uses 4,096-byte sectors. It reports 67,108,864-byte
`boot_a`/`boot_b` and `vendor_boot_a`/`vendor_boot_b` partitions;
8,388,608-byte `init_boot_a`/`init_boot_b`, `dtbo_a`/`dtbo_b`, `vbmeta_a`,
and `vbmeta_system_a` partitions; and a 73,367,552-byte `metadata` partition.
Its `userdata` entry is only a 4,096-byte placeholder in this package, so it
must not be used as the device's actual data partition size.

The boot image has header version 4, a 14,047,446-byte kernel, and no ramdisk.
The vendor boot image has header version 4, a 327,296-byte DTB, and normal and
recovery vendor ramdisk fragments. A/B `boot`, `init_boot`, `vendor_boot`,
`dtbo`, `vbmeta`, and `vbmeta_system` exist in the stock package.

The firmware's `flashfile.xml` includes erase operations for persistent
partitions, including `userdata` and `metadata`. It is a reference for image
names and partition layout; it is not a bring-up procedure.

## Source and binary boundary

The Motorola kernel and device-module trees are pinned in
`local_manifests/vienna-sources.xml` and `sources.lock.json`. The latter tree
refers to additional MediaTek source under `vendor/mediatek`, which is not in
these public clones. Building its full module set from the available sources
has not been established. The matching stock `vendor_dlkm` and `system_dlkm`
images are available as binary inputs. A kernel build and module compatibility
still require verification; neither has been tested on this phone.

The extracted `vendor/etc/vintf/manifest.xml` declares target level 8 and
includes radio, camera, audio, graphics, Bluetooth, Wi-Fi, GNSS, NFC, keymint,
and fingerprint HALs. The extracted `vendor/etc/fstab.mt6878`, VINTF files,
init scripts, HAL binaries, and both module partitions are the starting inputs
for the device tree and proprietary file list. Keep the extracted OEM binaries
in ignored `stock-firmware/`; do not commit them to this source repository.
