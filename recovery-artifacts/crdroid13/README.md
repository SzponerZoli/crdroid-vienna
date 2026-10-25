# crDroid 13 (Android 17) flash set for XT2409-1 RETEU — NOT YET FLASHED

Built 2026-10-25 from `crdroid17/` (manifest 17.0, `CP2A.260605.016`, userdebug,
test keys). Host-validated only; it has never booted.

## Images

Use the **target-files `IMAGES/` copies** for system, system_ext and product.
`out/target/product/vienna/{system,system_ext,product}.img` differ (packaging
regenerates them) and do **not** match `vbmeta_system.img`.

`IMAGES/` = `crdroid17/out/target/product/vienna/obj/PACKAGING/target_files_intermediates/lineage_vienna-target_files/IMAGES/`

| Partition | File | SHA-256 |
| --- | --- | --- |
| system | `IMAGES/system.img` | `2eaf42f389ecf842b7cd2bc28e7d1f97ac747992476a7939e67e8e5fab6240a0` |
| system_ext | `IMAGES/system_ext.img` | `8673f72d33356152ce4acb134bc3bb46fd77008476d155aebe3997df4c311b42` |
| product | `IMAGES/product.img` | `6c0aa60181d84a0e0e2d27bafc49cf139ff4ca98ac1e4a64707ae9ff66942b95` |
| vbmeta_system | `IMAGES/vbmeta_system.img` | `efda06eb09e85a487589c46db7167a3b016fc500cee61f1c202a610a658a0f3c` |
| vbmeta | `vbmeta-crdroid13.img` (this dir) | `b56d36deeef5bf58cbf565b9ab13c085ffadeea96b73a955a836f33b7d96d269` |

`vbmeta-crdroid13.img` = `../clean/clean-vbmeta-crdroid-callfix.img` with the
product descriptor replaced from `IMAGES/product.img`
(`tools/update_root_vbmeta_product.py`). It still covers the stock boot,
init_boot, dtbo, vendor, vendor_dlkm, system_dlkm and the clean recovery
`../clean/clean-vendor_boot.img`
(`652af86c0e8fbbacebd468ef9334eb400a4b47005ac9a81d6697255ff3a442c2`), which
must stay in `vendor_boot_a`. `avbtool verify_image --follow_chain_partitions
--expected_chain_partition vbmeta_system:2:<testkey>` passed for all of them.

## Host checks passed

- `check_target_files_vintf -v`: COMPATIBLE (stock vendor/ODM, SKU `dns`,
  kernel 6.1.141, FCM level 8, APEXes activated).
- Root and child rollback index 25, `HAB_META`/`KERN_PROT_META` present,
  super groups `main_a`/`main_b` at 23,083,352,064 bytes.
- No property_contexts duplicates against stock vendor/ODM.

## Draft flash plan (slot A, needs owner approval)

Preconditions: current backup; decision on wiping `/data` (Android 16 → 17
data upgrade with the same test keys is untested; there is no way back to
crDroid 12 without a wipe once Android 17 has touched `/data`); check the
phone over ADB (slot, boot state, current `vbmeta_a`).

```sh
adb reboot fastboot                        # userspace fastbootd
fastboot getvar current-slot               # expect a
fastboot flash system IMAGES/system.img
fastboot flash system_ext IMAGES/system_ext.img
fastboot flash product IMAGES/product.img
fastboot flash vbmeta_system IMAGES/vbmeta_system.img
fastboot flash vbmeta recovery-artifacts/crdroid13/vbmeta-crdroid13.img
# optional, if wiping: fastboot -w
fastboot reboot
```

Slot B currently holds a failed sideload test, not stock, so it is not a
fallback. Return path to crDroid 12: reflash its system/system_ext/product,
`vbmeta_system` and `../clean/clean-vbmeta-crdroid-callfix.img`, then wipe.
