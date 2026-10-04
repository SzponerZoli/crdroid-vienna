# Working Lineage recovery for XT2409-1 RETEU (`W1UIS36H.39-25-8`)

> The image files described here are **not published**: they are built from
> Motorola stock firmware and contain proprietary content. This file is kept as
> a record of what was built and tested.

**Status (2026-10-03):** boots on the owner's phone (slot A) to the Lineage
recovery UI. Built from the stock `vendor_boot` with only the recovery
ramdisk fragment changed. Only for firmware `W1UIS36H.39-25-8`.

| File | SHA-256 |
| --- | --- |
| lineage-vienna-recovery-v1-vendor_boot.img | `05a28798033879812f490999f6be33f01434ff0c1cd5f168e9616c2d758b7659` |
| lineage-vienna-recovery-v1-vbmeta.img | `302c0ea8ff7d4376839c67ac9676bbb6da7155e2dcbbf95efd5a8c0163767a53` |

Flash both to the **same slot** from bootloader fastboot, vbmeta first:

```sh
fastboot flash vbmeta_a recovery-artifacts/working/lineage-vienna-recovery-v1-vbmeta.img
fastboot flash vendor_boot_a recovery-artifacts/working/lineage-vienna-recovery-v1-vendor_boot.img
```

Enter it from the bootloader menu ("Recovery mode"). The vbmeta keeps every
stock descriptor except the `vendor_boot` hash, signed with the AOSP test
key (accepted by the unlocked bootloader; Android still boots normally).
Restore stock with the commands in `../README.md` (stock vbmeta first).

## How it works

The phone's stock recovery programs and libraries live in the **normal**
vendor ramdisk; the recovery fragment is overlaid on it. The fragment here is
Motorola's stock recovery fragment plus:

- `system/bin/recovery.real`: crDroid/Lineage recovery from
  `crdroid/out-recovery/.../recovery/root/system/bin/recovery`.
- `system/lib64/vienna-recovery/`: its full non-bionic dependency closure (40
  libraries plus `librecovery_ui_ext.so`) from the same build. Stock
  `init`/`adbd` keep Motorola's libraries.
- `system/bin/recovery`: a 1.7 KB static wrapper (`rwrap.c`) that redirects
  stdout/stderr to `/tmp/rerr.log` and execs `recovery.real`.
- `system/etc/init/hw/init.rc`: stock plus
  `setenv LD_LIBRARY_PATH /system/lib64/vienna-recovery` for the recovery
  service and `setprop sys.usb.config adb` on boot.
- Lineage `res/` UI resources.

## Why the earlier images failed

1. They ran the crDroid recovery binary against Motorola's stock copies of 34
   of its 40 libraries (`libfs_mgr`, `libbase`, `libutils`, ...). Symbol
   names resolved, but C++ ABI/layout differences crashed it immediately
   after it created `/tmp/recovery.log` (the log stayed 0 bytes).
2. With private libraries and `LD_LIBRARY_PATH` alone, init's transition into
   the `recovery` domain sets `AT_SECURE` (stock policy has no `noatsecure`),
   so bionic ignores `LD_LIBRARY_PATH`; recovery exited with status 1 every
   5 s.
3. The wrapper is already in the `recovery` domain, so its `execve` has no
   transition, `AT_SECURE` is 0, and the private libraries load.

Rebuild: `cpio_add.py` (in this directory) adds files/directories to the
stock fragment (`lz4 -dc` of stock `vendor_ramdisk01`); recompress with
`lz4 -l -12`, then `tools/assemble_recovery_vendorboot.py --fragment` and
`tools/make_matching_recovery_vbmeta.py`. The bisect images T1–T10 in
`../bisect/` document each step.
