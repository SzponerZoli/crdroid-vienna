# Early bring-up notes (2026-09-28 to 2026-10-03)

> **Historical.** This was the project README before crDroid first booted on
> 2026-10-03. It is kept for its research trail: source pinning, firmware
> inventory, VINTF/SELinux checks and failed recovery experiments. For the
> current state see the [README](../README.md) and the
> [bring-up log](BRINGUP_LOG.md).


**Handoff at the time (2026-10-03):** Read the [bring-up log](BRINGUP_LOG.md)
first. It records the updated stock firmware, failed recovery tests, corrected
intermediate AVB/super metadata, and the interrupted target-files packaging.
Some historical notes below still describe the phone before its firmware
update. There is no tested crDroid release or working custom recovery.

Target: **crDroid 12 (Android 16)** for the Motorola Edge 50 Neo (XT2409 family, MediaTek MT6878). A prototype device product is under `device/motorola/vienna/`. Its three system images and a candidate A/B OTA ZIP now build successfully. It has not passed an on-device test and is **not ready to flash**.

See [the roadmap](../ROADMAP.md) for current milestones and how to check a running build.

The connected test phone reports **XT2409-1 / RETEU / W1UIS36H.39-17-8**, Android 16, Linux 6.1.141, launch API 34, A/B slots, and virtual A/B updates. Its bootloader is unlocked (`ro.boot.flash.locked=0`); [the latest read-only state](../research/connected-device-state.md) confirms it is still on the older firmware. The earlier full report is saved locally under `stock-info/` and ignored by Git.

The Edge 50 Neo also appears in public sources under the `vienna` codename. Its images and kernel releases must not be assumed compatible with the Edge 50 Neo. The phone's model, build fingerprint, partition layout, and kernel release need to be matched before selecting source and blobs.

## Current findings

| Item | Evidence | Status |
| --- | --- | --- |
| Chipset and launch OS | [Motorola specifications](https://en-in.support.motorola.com/app/answers/detail/a_id/183718/~/specifications---motorola-edge-50-neo) | Dimensity 7300 / Android 14 |
| Codename | [Motorola Edge 50 Neo build fingerprint](https://github.com/MotorolaMobilityLLC/kernel-mtk/issues/247) | `vienna` |
| Existing recovery work | [Community recovery tree](https://github.com/ChimpanziCloud/android_device_motorola_vienna) | Useful for research; not a ROM device tree |
| Current kernel source | [Motorola kernel-mtk](https://github.com/MotorolaMobilityLLC/kernel-mtk) and [device modules](https://github.com/MotorolaMobilityLLC/kernel-kernel_device_modules-6.1) | `MMI-W1UIS36H.39-17-8` tags exist in both repositories |
| Newer XT2409-1 RETEU firmware | [Public firmware index](https://mirrors.lolinet.com/firmware/lenomola/2024/vienna/official/3GB/) | `W1UIS36H.39-25-8`; matching Motorola kernel and module source tags exist |
| crDroid base | [crDroid `16.0` manifest](https://github.com/crdroidandroid/android) | crDroid 12 / Android 16 |

The phone's stock fstab confirms dynamic partitions, F2FS userdata and metadata, and file encryption with `inlinecrypt`. Its block map confirms A/B `boot`, `init_boot`, `vendor_boot`, `dtbo`, and `vbmeta` partitions. The community recovery tree's README marks `/data` decryption as unfinished, and its `BoardConfig.mk` has recovery-specific settings that are unsuitable to copy into a crDroid port.

The exact-model XT2409-1 RETEU firmware package has been downloaded, verified,
and extracted under ignored `stock-firmware/`. It is **W1UIS36H.39-25-8**,
newer than the phone's current **W1UIS36H.39-17-8**. Before testing a ROM
based on these binaries, the phone's stock base must be checked and made
compatible. See [the pinned inputs](../sources.lock.json),
[the local manifest](../local_manifests/vienna-sources.xml), and
[device facts](../research/device-facts.md).

The firmware ZIP is 6,903,313,944 bytes with SHA-256
`f38e07b14b1c984c44b736d7608d06be4e352b347e2ae554a470b728e81236dd`.
The public Motorola kernel and device-module sources are checked out locally
at matching `MMI-W1UIS36H.39-25-8` tags. The module source tree references
additional MediaTek sources absent from these public checkouts; full source
buildability has not been established.

## Source preparation

The [crDroid 16.0 manifest](https://github.com/crdroidandroid/android/tree/16.0)
is the Android 16 base for this port. Its observed commit and the two Motorola
source commits are in [sources.lock.json](../sources.lock.json). The
[local manifest](../local_manifests/vienna-sources.xml) adds those Motorola
research trees under `kernel/motorola/`, plus LineageOS MediaTek hardware and
policy dependencies, to the crDroid checkout. It does not supply proprietary
MediaTek module source or a ready-made, tested port.

The ignored `crdroid/` checkout is initialized at the pinned `16.0` manifest
commit and its 1,184 projects synced successfully. A
[resolved manifest](../research/crdroid-12.12-resolved.xml) records every checked
out revision. The pinned Motorola projects can also be inspected under ignored
`stock-source/`. The prototype product passes
`lunch lineage_vienna bp4a userdebug`. A prototype system, system_ext, and
product image build can be run with `bash tools/build_systemimage.sh`; it writes
`crdroid/out/build-systemimage.log` and a numeric
`crdroid/out/build-systemimage.exit-code` when finished. The build can take
several hours.

The first `system`, `system_ext`, and `product` image build passed on
2026-09-30. Image sizes, SHA-256 digests, EROFS checks, and the remaining
install risks are recorded in [the prototype build report](../research/prototype-image-build.md).
Target-files packaging also passed; that archive is an intermediate input to
OTA generation, not an installable ROM.

The follow-up image build added the stock VINTF compatibility matrices and
VNDK 31/33/34 APEXes. A host check of its framework files against the exact
stock vendor and ODM VINTF files passed for the phone's `dns` SKU. The rebuilt
target-files package also includes those stock VINTF files and records `dns`
for package-level checks. Its ZIP integrity and prototype AVB chain passed.
Android's APEX-aware target-files VINTF check also returned `compatible` for
the `dns` SKU, first API level 34, and packaged kernel requirements.

A [candidate A/B OTA ZIP](../research/prototype-image-build.md#candidate-ab-ota-zip)
has also built and passed a ZIP integrity check. It is signed with Android's
development test key and has not been installed or booted. The connected
phone's firmware is older than the boot/vendor images in the ZIP, so its
installation path and recovery behavior still need validation.

The device tree also carries the exact `recovery.fstab` extracted from the
pinned stock `vendor_boot.img` as a recovery reference; see the
[device tree notes](../device/motorola/vienna/README.md). Because no new recovery
image is built, Android's A/B OTA target is explicitly enabled. OTA generation
remains experimental and does not imply a safe installation path.

The first full image build exposed an unrelated crDroid SystemUI Kotlin
signature mismatch. The two `onAlbumArtChanged` overrides now accept the
nullable `Drawable?` declared by `MediaDataListener`; their storage and use
sites already accept null. The change is saved as
[`frameworks-base-systemui-nullable-album-art.patch`](../patches/frameworks-base-systemui-nullable-album-art.patch)
and applied in the active checkout. After resyncing `frameworks/base`, reapply
it from this directory with:

```sh
git -C crdroid/frameworks/base apply ../../../patches/frameworks-base-systemui-nullable-album-art.patch
```

The next full build reached WebView packaging and found that the arm64
`webview.apk` was still a Git LFS pointer. Fetch the real prebuilt before
building (or after a checkout that restores the pointer):

```sh
python3 tools/fetch_lfs_object.py crdroid/external/chromium-webview/prebuilt/arm64/webview.apk
```

The helper verifies the downloaded file against the pointer's size and
SHA-256 before replacing it. The other architecture APKs remain pointers;
this arm64 product does not use them.

Target-files packaging also needs the stock prebuilt boot images. The product
disables vendor_boot rebuilding so Android stages the exact-model prebuilt.
The local Android make patch stages prebuilt `init_boot.img` and the verified
stock vendor build properties and VINTF metadata before target-files assembly.
It also handles partitions that have no file tree in the package and records
the stock ODM `dns` SKU. After resyncing `build/make`,
reapply it with:

```sh
git -C crdroid/build/make apply ../../../patches/build-make-prebuilt-target-files.patch
```

The [prototype product](../device/motorola/vienna/README.md) is configured to build crDroid's
system, system_ext, and product components around the exact-model stock boot,
vendor, DTBO, and kernel module images. Copy the source files to
`crdroid/device/motorola/vienna/` and run
`python3 tools/stage_stock_images.py` to place the checksum-verified images
under its ignored `prebuilts/` directory. The host image build has passed;
the resulting images are not approved for flashing.

The [firmware inventory](../research/firmware-inventory.json), generated by
`python3 tools/inventory_firmware.py`, lists HAL services and libraries,
VINTF files, init configuration, kernel modules, firmware, and permission
files from the six extracted logical partitions. It is a candidate list for
curation, not a drop-in proprietary extraction list.

The device tree has an initial [proprietary file list](../device/motorola/vienna/proprietary-files.txt)
and a standard `extract-files.py` entry point. All 49 entries were extracted
from the exact XT2409-1 RETEU stock dump into the ignored local
`crdroid/vendor/motorola/vienna/` tree. The initial 42 files' SHA-256
digests match the stock files except for two documented ELF fixes: `libsink.so` is renamed to
`libsink-mtk.so`, and `libimsma.so` is linked to the renamed library. The
generated text rules are saved under
[`vendor/motorola/vienna/`](../vendor/motorola/vienna/README.md) and inherited by
the prototype product. Their build integration passed, but runtime behavior remains unverified. The selected native
libraries have no additional direct dependencies elsewhere in the stock
`system_ext/lib64` directory. This does not establish boot or radio
compatibility.

Five extracted MediaTek APKs declare `android.uid.phone`; their generated
imports use the crDroid platform key. The remaining three APKs retain their
stock signatures. `ImsService.apk` also needs Motorola's `moto-telephony`
shared library; its JAR and declaration are included. These choices still
need runtime validation. Four MediaTek framework JARs from stock
`bootclasspath.pb` are declared in the prototype's boot classpath.

A [static SELinux cross-reference report](../research/sepolicy-crossrefs.json)
finds 91 stock `system_ext` policy names mentioned by the prebuilt vendor
policy; 64 are absent from the generic MediaTek source declarations. This name
scan is only a review aid. The focused source policy build now passes, and
[`check_stock_vendor_sepolicy.py`](../tools/check_stock_vendor_sepolicy.py)
successfully combined the built crDroid platform, system_ext, and product CIL
with the **actual stock vendor CIL** and its 34.0 compatibility mapping using
Android init's split-policy compile options. The host result is recorded in
[`sepolicy-stock-vendor-compat.json`](../research/sepolicy-stock-vendor-compat.json).
It does not validate every file or service label or the policy's behavior on
the phone.

The [stock `system_ext` service inventory](../research/system-ext-services.json),
generated by `python3 tools/audit_system_ext_services.py`, records init
services, their executable dependencies, and VINTF fragments. It finds 12
existing stock service binaries outside the current proprietary list. These
are candidates for review, not an automatic extraction list: for example,
stock `mediahelper` and AOSP `mediaserver` both declare the `media` service.

The [stock AVB inventory](../research/avb-stock.json), generated by
`python3 tools/audit_stock_avb.py`, records the root and chained vbmeta
descriptors. Stock uses SHA256_RSA2048, rollback index 25, and a
`vbmeta_system` chain at location 2. The prototype build key differs from
Motorola's stock key; its AVB chain and install procedure are not validated.

## Collect current stock information

This step reads system properties and public configuration files through ADB. It does not root, write to, or reboot the phone.

1. On the phone, enable **Developer options** and **USB debugging**.
2. Connect it by USB and accept the computer's debugging authorization prompt.
3. From this repository, run:

   ```sh
   python3 tools/collect_stock_info.py
   ```

The command creates a timestamped directory under `stock-info/`. Review it before sharing; the report intentionally avoids serial numbers and account data, but build fingerprints can identify a software variant. If ADB reports `unauthorized`, accept the prompt on the phone and rerun it.

## Next build milestones

1. Expand the exact-model proprietary list beyond cellular components and validate APK signing, framework class paths, and native ABI compatibility.
2. Complete VINTF, init, and enforcing SELinux policy for the crDroid device tree.
3. **Done:** Resolve build errors and build the first three prototype images on the host.
4. With the already unlocked bootloader, establish a compatible stock firmware base and test recovery, boot, encryption, radio and emergency calls, Wi-Fi, Bluetooth, GPS, camera, audio, NFC, fingerprint, sensors, and OTA updates on the actual phone.

No image should be flashed until it has been built from a matched stock firmware base and reviewed for the exact device variant. Unlocking the bootloader erases user data.
