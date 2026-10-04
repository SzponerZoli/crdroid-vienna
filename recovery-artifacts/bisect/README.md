# Recovery bisect images (host-built 2026-10-03, not yet device-tested)

> The image files described here are **not published**: they are built from
> Motorola stock firmware and contain proprietary content. This file is kept as
> a record of what was built and tested.

For XT2409-1 RETEU `W1UIS36H.39-25-8` only. Each pair is flashed together to
the **active slot** from bootloader fastboot, then recovery is entered.

| Test | vendor_boot change | Question answered |
| --- | --- | --- |
| T1 | Stock recovery fragment, same content, recompressed with `lz4 -l -9` | Can any re-hashed vendor_boot plus test-key vbmeta boot recovery mode? |
| T2 | Stock fragment plus one 35-byte text file `/bisect-t2.txt` | Does changing the fragment's contents break it? |

Expected success: stock Motorola recovery appears ("No command"), as with the
original images. Images:

| File | SHA-256 |
| --- | --- |
| t1-vendor_boot.img | `1d237d707b756ccbb80fe5df50f74bd0c470f3d64c56501167d6aff68f715abf` |
| t1-vbmeta.img | `71d19636b5a3dc9fd8860aa8f9370dc1c480274892a2d207aac61a216c05ddfc` |
| t2-vendor_boot.img | `5b5d45c62224d27c0cf0516b20d5c65156030f5449f58b0afe0d3687c1b121ed` |
| t2-vbmeta.img | `62f5619aae9c9a0f6cdcb8635a5ca85f2bdb3d029a53cdfbd6d12b7dc4a290ce` |

Restore afterwards (slot A shown; **vbmeta first**):

```sh
fastboot flash vbmeta_a stock-firmware/extracted/vbmeta.img
fastboot flash vendor_boot_a crdroid/device/motorola/vienna/prebuilts/vendor_boot.img
fastboot reboot
```
