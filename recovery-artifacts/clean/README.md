# Clean Lineage recovery for XT2409-1 RETEU (`W1UIS36H.39-25-8`)

> The image files built here are **not published**: they contain Motorola's
> stock vendor ramdisk. Build them yourself with the steps below.

**Status (2026-10-04):** in daily use on the developer's phone (slot A). The menu
works, "Reboot system now" and "Advanced → Reboot to bootloader" work, and the
crDroid system boots normally with this `vendor_boot`.

## What it is

The phone has no recovery partition. Recovery is the second ramdisk
(fragment) of `vendor_boot`, overlaid on the normal vendor ramdisk.
[`tools/make_recovery_fragment.py`](../../tools/make_recovery_fragment.py)
keeps Motorola's stock fragment, init, adbd and **stock enforcing SELinux
policy**, and adds the crDroid/Lineage recovery binary, its private library
closure, a small exec wrapper ([`rwrap.c`](../working/rwrap.c)), the Lineage
UI resources and two `init.rc` lines (library path, ADB on). The normal
vendor ramdisk and the kernel command line stay byte-identical to stock.

It needs [`patches/bootable-recovery-vienna-fixes.patch`](../../patches/bootable-recovery-vienna-fixes.patch):

- `recovery_main.cpp`: clear `LD_LIBRARY_PATH` after start, so helpers such
  as `minadbd` (sideload) use the stock ramdisk libraries.
- `volume_manager/NetlinkManager.cpp`: the stock policy denies the recovery
  a uevent netlink socket, so the volume watcher never starts. Its `stop()`
  then dereferenced a null handler on every reboot/power-off, the recovery
  crashed with SIGSEGV and init restarted it ("reboot does nothing"). Start
  and stop are now safe when the socket is unavailable. Only hot-plug
  detection of USB drives inside recovery is lost.

Known limitation: no `adb shell` in recovery (the stock policy has no `su`
domain). `adb reboot` and `adb reboot bootloader` work; sideload is untested.

## Build

```sh
bash tools/build_recovery.sh            # lunch lineage_vienna_recovery; mka vendorbootimage
STOCK=crdroid/device/motorola/vienna/prebuilts/vendor_boot.img
python3 tools/make_recovery_fragment.py --stock-vendor-boot $STOCK \
    --recovery-root crdroid/out-recovery/target/product/vienna/recovery/root \
    --clang $PWD/crdroid/prebuilts/clang/host/linux-x86/clang-r574158/bin/clang \
    --out recovery-artifacts/clean/recovery-fragment.cpio.lz4
python3 tools/assemble_recovery_vendorboot.py --stock $STOCK \
    --fragment recovery-artifacts/clean/recovery-fragment.cpio.lz4 \
    --out recovery-artifacts/clean/clean-vendor_boot.img
```

## Root vbmeta

The root `vbmeta` carries the `vendor_boot` digest. Starting from the root
vbmeta that boots your crDroid (see the top-level README), replace only that
digest:

```sh
python3 tools/make_matching_recovery_vbmeta.py \
    --stock-vbmeta vbmeta-crdroid.img --stock-vendor-boot $STOCK \
    --recovery-vendor-boot recovery-artifacts/clean/clean-vendor_boot.img \
    --out vbmeta-crdroid-recovery.img
```

`--stock-vendor-boot` must be the `vendor_boot` that the input vbmeta was made
for (the stock image, unless you start from another recovery's vbmeta).

## Flash (bootloader fastboot, active slot, vbmeta first)

```sh
fastboot flash vbmeta_a vbmeta-crdroid-recovery.img
fastboot flash vendor_boot_a recovery-artifacts/clean/clean-vendor_boot.img
fastboot reboot recovery
```

To go back to Motorola's recovery, flash the stock `vendor_boot` and the
vbmeta made for it.
