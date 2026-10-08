# crDroid 12 for Motorola Edge 50 Neo (`vienna`)

> [!CAUTION]
> **This port is "vibe coded": it was built almost entirely by AI coding
> assistants** (ChatGPT, then Claude), directed and tested by the owner on one
> phone. The device tree, patches, SELinux rules, tools and documentation were
> written by AI and have **not been reviewed by an experienced Android or
> MediaTek developer**. Expect mistakes the AI did not notice. Treat everything
> here as experimental, check it yourself before relying on it, and do not use
> this ROM on a phone you cannot afford to lose or restore.

An unofficial port of **crDroid 12 (Android 16)** to the Motorola Edge 50 Neo,
**XT2409-1 RETEU** (MediaTek Dimensity 7300 / MT6878). crDroid's system,
system_ext and product images run on top of the phone's unmodified stock
Motorola boot, vendor and kernel images (firmware `W1UIS36H.39-25-8`).

> **Status: experimental, single-device tested.** It runs as the daily system on
> one XT2409-1 RETEU. A fastboot package is available under
> [Releases](https://github.com/SzponerZoli/crdroid-vienna/releases); there is no
> OTA zip yet. Read the whole [Installing](#installing) section before you touch
> your phone; you need to be comfortable restoring stock firmware with fastboot.
> **Only the XT2409-1 RETEU is supported** (see [Supported models](#supported-models)).

> [!WARNING]
> **Use at your own risk.** Unlocking the bootloader and flashing this ROM can
> void your warranty, erase your data, and leave your phone unbootable
> ("bricked"). This is an unofficial project, not affiliated with Motorola,
> MediaTek or the crDroid team. It is provided "as is" without warranty of any
> kind, and the authors accept no liability for any damage or data loss (see
> sections 7 and 8 of the [license](LICENSE)). Back up everything and keep the
> stock firmware for your exact model at hand before you start.

## Supported models

| Model | Status |
| --- | --- |
| XT2409-1 **RETEU** on stock `W1UIS36H.39-25-8` | Supported (the developer's phone) |
| XT2409-1 RETEU on another firmware version | Update to `W1UIS36H.39-25-8` first |
| Any other variant (other regions, other XT2409-x) | **Not supported.** Do not flash the release |

The release only replaces `system`, `system_ext` and `product`; it reuses the
phone's stock kernel, `boot` and `vendor` images. Its root `vbmeta` carries
the hashes of the RETEU `W1UIS36H.39-25-8` images, and its `vendor_boot` comes
from that firmware too. On other stock firmware it will most likely hang at
the Motorola logo, and flashing the RETEU `vendor_boot` replaces your own.
The APN and VoLTE settings were only tuned for Hungarian carriers.

Other variants may be portable by building against their own stock firmware
(see [Building](#building)), but nobody has tried it. If you own one, open an
issue with your model number (`ro.boot.hardware.sku`), region and firmware
version instead of flashing, and keep your stock firmware at hand.

## What works

Tested on 2026-10-04 on XT2409-1 RETEU, stock base `W1UIS36H.39-25-8`:

| Area | Status | Notes |
| --- | --- | --- |
| Boot, setup wizard, ADB | Works | SELinux enforcing |
| Mobile data, both SIMs (DSDS) | Works | LTE on both SIMs; tested with Yettel HU and Telekom HU |
| Voice calls, VoLTE | Works | MediaTek IMS on both SIMs; carrier VoLTE config for 216-01 and 216-30 |
| Camera | Works | Stock Motorola camera stack |
| GPS / location | Works | microG is the network location provider |
| Fingerprint (under-display) | Works | Uses the Moto panel's `HIGH_BRIGHT_FOD` mode with a dim layer, like stock |
| Face unlock | Works | |
| Bluetooth, incl. audio | Works | A2DP hardware offload is disabled (software encoding) |
| microG | Bundled | GmsCore 0.3.17 + Companion, signature spoofing via crDroid |
| Video calls (ViLTE) | Works | |
| NFC | Works | |
| Battery life | Good | Comparable to stock in the developer's use |
| Lineage recovery (optional) | Works | Enforcing stock SELinux policy; menu, reboot and sideload install work; no `adb shell` ([details](recovery-artifacts/clean/README.md)) |

Not tested yet: Wi-Fi calling, OTA updates. Untested does not mean broken.
Reports are welcome.

### Known issues

- **The Lineage recovery is built separately** and flashed into
  `vendor_boot`; see [its README](recovery-artifacts/clean/README.md). The
  install steps below keep Motorola's stock recovery.
- **A2DP hardware offload is off.** With offload on, headphones connect but
  play silence. Software encoding works but may use slightly more power.
- **Fingerprint dim level is estimated.** During a scan the rest of the screen
  may look slightly brighter or darker than normal
  (`config_udfpsMotoPanelHbmNits` in the device overlay).
- **APNs for other countries come from LineageOS** and may need manual
  correction, as Yettel HU did (see `patches/vendor-apn-yettel-stock-apns.patch`).

## Repository layout

| Path | Contents |
| --- | --- |
| `device/motorola/vienna/` | Device tree: product makefiles, overlays, VINTF matrices, SELinux, microG integration |
| `vendor/motorola/vienna/` | Generated build rules for the proprietary files (the files themselves are **not** included) |
| `patches/` | Changes to crDroid source repos, one patch per repo and topic |
| `local_manifests/` | Extra repo projects (Motorola kernel sources, LineageOS MediaTek HALs) |
| `sources.lock.json` | Pinned crDroid manifest, stock firmware and image checksums |
| `tools/` | Build, AVB/vbmeta, audit and firmware helper scripts |
| `research/` | Firmware inventory, SELinux/VINTF audits, recovery and fastbootd assessments |
| `docs/` | [Bring-up log](docs/BRINGUP_LOG.md) (newest at the end) and [early notes](docs/early-bringup.md) |

No Motorola or MediaTek binaries are in this repository. You extract them
yourself from the official firmware package for your phone.

## Building

The build is reproducible but not yet a one-command process. Expect a source checkout
of several hundred GB and several hours of build time.

1. **Sync crDroid 16.0** at the commit pinned in `sources.lock.json`, and copy
   `local_manifests/vienna-sources.xml` into `.repo/local_manifests/` before
   syncing. This README assumes the checkout is in `crdroid/` next to it.
2. **Copy the device tree** into the checkout:
   `cp -r device/motorola/vienna crdroid/device/motorola/`
3. **Apply the patches** (each file name says which repo it belongs to; see the
   table in the [bring-up log](docs/BRINGUP_LOG.md#source-patches-2026-10-04)):

   ```sh
   git -C crdroid/build/make apply "$PWD"/patches/build-make-prebuilt-target-files.patch
   git -C crdroid/device/lineage/sepolicy apply "$PWD"/patches/device-lineage-sepolicy-drop-camera-aux-prop.patch
   git -C crdroid/device/mediatek/sepolicy_vndr apply "$PWD"/patches/device-mediatek-sepolicy_vndr-drop-pco5-prop.patch
   git -C crdroid/frameworks/base apply "$PWD"/patches/frameworks-base-systemui-nullable-album-art.patch
   git -C crdroid/frameworks/base apply "$PWD"/patches/frameworks-base-ims-mtk-constructors.patch
   git -C crdroid/frameworks/base apply "$PWD"/patches/frameworks-base-systemui-udfps-moto-panel-hbm.patch
   git -C crdroid/frameworks/opt/telephony apply "$PWD"/patches/frameworks-opt-telephony-telephonymetrics-stub.patch
   git -C crdroid/vendor/apn apply "$PWD"/patches/vendor-apn-yettel-stock-apns.patch
   git -C crdroid/bootable/recovery apply "$PWD"/patches/bootable-recovery-vienna-fixes.patch
   ```

4. **Fetch the arm64 WebView** (the checkout contains a Git LFS pointer):
   `python3 tools/fetch_lfs_object.py crdroid/external/chromium-webview/prebuilt/arm64/webview.apk`
5. **Get the stock firmware** `W1UIS36H.39-25-8` for XT2409-1 RETEU (URL and
   SHA-256 in `sources.lock.json`) and unpack it under `stock-firmware/`. Then:
   - extract the proprietary files with `device/motorola/vienna/extract-files.py`
     (list in `proprietary-files.txt`)
   - stage the stock boot/vendor images with `python3 tools/stage_stock_images.py`
     (verifies every checksum against the lock file)

   The exact unpacking layout is described in the
   [early notes](docs/early-bringup.md#source-preparation).
6. **Download microG** as described in
   [`device/motorola/vienna/microg/README.md`](device/motorola/vienna/microg/README.md)
   and check the SHA-256 sums.
7. **Build:**

   ```sh
   bash tools/build_systemimage.sh target-files-package
   cat crdroid/out/build-systemimage.exit-code   # 0 = success
   ```

   This builds `system`, `system_ext`, `product`, `vbmeta_system` and the
   target-files intermediates, whose root `vbmeta` the install step needs.
   For later rebuilds, `systemimage systemextimage productimage
   vbmetasystemimage` is enough.

## Installing

### Fastboot package (recommended)

A prebuilt package (`crdroid-12-vienna-<date>-fastboot.zip`) contains the
tested image set, `flash.sh` (Linux/macOS), `flash.bat` (Windows) and a
README. With the phone in bootloader mode:

```sh
./flash.sh --wipe     # from stock or another ROM (formats userdata)
./flash.sh            # updating an existing install of this build
```

The script verifies the image checksums, flashes the root `vbmeta` and the
Lineage recovery (`vendor_boot`) in the bootloader, then `system`,
`system_ext`, `product` and `vbmeta_system` in fastbootd, and reboots. The
same requirements as below apply; in particular the active slot must run stock
`W1UIS36H.39-25-8`. `flash.sh` was tested on the developer's phone;
`flash.bat` uses the same steps but is untested and skips the checksum check.

The package is built with `tools/make_fastboot_package.py`, which refuses an
image set whose vbmeta digests do not match. A sideloadable OTA zip installs
but does not boot yet (see the [bring-up log](docs/BRINGUP_LOG.md)).

### From your own build

**Requirements:**

- XT2409-1 RETEU with an **unlocked bootloader**.
- The **active slot runs stock `W1UIS36H.39-25-8`.** crDroid reuses that slot's
  boot, vendor and kernel images. Other firmware versions are untested.
- A full backup. Coming from stock, **userdata must be wiped**.
- The stock firmware package at hand, to restore if anything goes wrong.

**1. Make the root vbmeta.** The bootloader checks the product image's digest
in the root `vbmeta`. Generate one that keeps Motorola's boot and vendor
descriptors and points at the crDroid images:

```sh
OUT=crdroid/out/target/product/vienna
python3 tools/make_stockboot_crdroid_vbmeta.py \
    --stock-root stock-firmware/extracted/vbmeta.img \
    --built-root $OUT/obj/PACKAGING/target_files_intermediates/lineage_vienna-target_files/IMAGES/vbmeta.img \
    --out vbmeta-crdroid-stage1.img
python3 tools/update_root_vbmeta_product.py \
    --root vbmeta-crdroid-stage1.img --product $OUT/product.img \
    --out vbmeta-crdroid.img
```

Every product.img rebuild needs a new root vbmeta. Otherwise the phone hangs
at the Motorola logo with no USB.

> The developer's phone boots with the Lineage recovery in `vendor_boot` and
> a matching root vbmeta. This exact stock-`vendor_boot`
> variant follows the same steps but **has not been booted yet**. If it hangs,
> restore stock (below) and report it.

**2. Flash** (replace `_a` with your active slot from
`fastboot getvar current-slot`):

```sh
adb reboot fastboot                      # userspace fastbootd
fastboot flash system_a        $OUT/system.img
fastboot flash system_ext_a    $OUT/system_ext.img
fastboot flash product_a       $OUT/product.img
fastboot flash vbmeta_system_a $OUT/vbmeta_system.img
fastboot reboot bootloader               # root vbmeta needs the bootloader
fastboot flash vbmeta_a vbmeta-crdroid.img
fastboot -w                              # wipe userdata (coming from stock)
fastboot reboot
```

The first boot takes about a minute to reach the setup wizard.

**Back to stock:** flash the stock `vbmeta` first, then the stock logical
partitions from the firmware package (`system`, `system_ext`, `product`,
`vbmeta_system`, ...) through fastbootd, and wipe data. Motorola's flashfile
XML in the firmware package lists every partition.

## Credits

- [crDroid](https://crdroid.net/) and [LineageOS](https://lineageos.org/) for
  the ROM, the MediaTek HALs and SELinux policy.
- [microG](https://microg.org/) for GmsCore and Companion.
- [Motorola Mobility](https://github.com/MotorolaMobilityLLC) for the
  published kernel sources.
- [ChimpanziCloud/android_device_motorola_vienna](https://github.com/ChimpanziCloud/android_device_motorola_vienna)
  for early recovery research on this codename.

## License

The device tree, tools, patches and documentation are under the
[Apache License 2.0](LICENSE). Patches to crDroid/LineageOS/AOSP projects
keep the licenses of the projects they modify. Proprietary Motorola and
MediaTek files are not part of this repository and are not covered by this
license.
