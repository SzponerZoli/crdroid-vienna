# Recovery artifacts

> The image files described here are **not published**: they are built from
> Motorola stock firmware and contain proprietary content. This file is kept as
> a record of what was built and tested.

`OrangeFox-R12.0-Unofficial-vienna.img` is a verified copy of the 2026-08-28
community release. **Do not flash it to the connected XT2409-1**: its packaged
kernel modules target `6.1.99`, while the phone runs `6.1.141`.

See [the assessment](../research/custom-recovery-assessment.md) for the image
hash, partition layout, and remaining recovery work.

`lineage-vienna-recovery-stock25-usb-vendor_boot.img` failed a slot A device
boot test on 2026-10-01: screen stayed off and USB showed repeated MediaTek
preloader starts. Stock `vendor_boot_a` was restored from fastboot. Motorola
stock recovery and then Android booted successfully. Do not flash this image.

`lineage-vienna-stockbased-vendor_boot.img` also failed a slot A recovery boot
test: the phone returned to MediaTek preloader. Stock `vendor_boot_a` was
restored and Android booted again. A later test with the matching test-key
`vbmeta` image below failed the same way. Both stock images were restored, and
ADB confirmed Android booted with build `W1UIS36H.39-25-8` and the original
Motorola `vbmeta` digest. Do not flash this image. It was
built for **XT2409-1 RETEU W1UIS36H.39-25-8**. It preserves Motorola's normal
ramdisk, DTB, bootconfig, recovery init, fstab, and SELinux policy. Its small
recovery fragment adds the Lineage recovery binary, required libraries and UI
resources. It passed host size and AVB hash checks. SHA-256:
`937a7c38e243bf2267b8907bddf1c52556713fc5acf403ecfbb177f3092edd91`.

`vbmeta-stock25-lineage-recovery-testkey.img` is a host-prepared AVB test
image for use only with the stock-based recovery image above. It preserves all
stock AVB descriptors, rollback index 25, and verification flags 0. The sole
descriptor change is the hash and size for the modified `vendor_boot`. The
root metadata is signed with the Android development test key because
Motorola's private signing key is unavailable. Its signature was verified on
the host. A test-key `vbmeta` with unchanged stock descriptors booted Android,
but this matching `vbmeta` plus the stock-based recovery image did not boot
recovery. Both stock images were restored. Do not flash this test pair. SHA-256:
`8585a195f66907548fdb26c48b9274afc9b398324ffc65219928accc1fede14f`.

Host ELF analysis found the stock-based recovery program had 14 unresolved
strong symbols against the stock recovery libraries, including newer libc++
and Binder APIs. `lineage-vienna-abi-compatible-vendor_boot.img` adds the
matching built `libc++.so`, `libbinder_ndk.so`, and `libbinder.so`. Its ELF
dependency closure passed with no missing libraries or strong symbols, and
the image passed host size and AVB checks. Its matching test-key root metadata
is `vbmeta-stock25-abi-compatible-recovery-testkey.img`. **This pair also
failed the slot A recovery boot test**: USB returned through MediaTek preloader
without ADB recovery. Stock `vbmeta_a` and `vendor_boot_a` were restored;
Android then booted with the expected stock build and Motorola `vbmeta`
digest. Do not flash this pair. Image SHA-256:
`784cf511bc12e11e5cae390cba9f409767640b8d04862f0e8c9ff3e68071b628`.
Matching `vbmeta` SHA-256:
`2cfbf615e4e5e88f8a3cd9af91d3b500ba36412f753f86b2d894263c9c69e8bb`.

The older `lineage-vienna-recovery-stock25-vendor_boot*.img` files are
superseded experiments and should not be flashed. The exact-model stock
restoration image is
`../crdroid/device/motorola/vienna/prebuilts/vendor_boot.img`, SHA-256
`a3876fb1d1aee3c62ba78037f67c207fa65cc50b607259559e6ef37737c7071f`.
The stock root vbmeta is `../stock-firmware/extracted/vbmeta.img`, SHA-256
`c0229c6cf41e3658366120c9e72ba8c497227cc85d1fbc9cdbcfa60b50ccec42`.
For a slot A test, restore it from bootloader fastboot with:

```sh
fastboot flash vbmeta_a stock-firmware/extracted/vbmeta.img
fastboot flash vendor_boot_a crdroid/device/motorola/vienna/prebuilts/vendor_boot.img
fastboot reboot
```

Flash stock `vbmeta` first: fastboot rejected the stock `vendor_boot` with
`Preflash validation failed` while the matching test-key `vbmeta` was still
installed, then accepted it after stock `vbmeta` was restored. Use only after
confirming the device and active slot. The Edge 50 Neo has no standalone
recovery partition.
