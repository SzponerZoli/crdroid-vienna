# Bring-up log: crDroid 12 port for Motorola Edge 50 Neo (`vienna`)

> Chronological engineering log of the bring-up, written as a working handoff
> between sessions. Newest entries are at the end. Paths such as `crdroid/`,
> `stock-firmware/` and `recovery-artifacts/` refer to local, unpublished
> directories (source checkout, Motorola firmware, built images).

Last audited **2026-10-03**. This document is the starting point for another
assistant. It records what was measured, built, flashed, restored, and left
unfinished. The objective is a bootable crDroid 12 / Android 16 port for the
owner's **Motorola Edge 50 Neo XT2409-1, RETEU**, plus a custom recovery if a
working one can be made. The Android product is named `lineage_vienna` because
crDroid uses Lineage build conventions; the intended ROM is **crDroid**.

**There is no tested, bootable crDroid release or working custom recovery. Do
not flash the old OTA ZIP, any image in `recovery-artifacts/`, or the host-only
metadata in `install-artifacts/`.** The latest full OTA is an outdated host
prototype. The latest target-files ZIP is 0 bytes after interrupted packaging.

## Phone and owner preferences

- The phone is XT2409-1 / RETEU, codename `vienna`, MediaTek MT6878, SKU
  `dns`, Android 16, launch API 34, A/B and virtual A/B. **Do not substitute
  an XT2409-6 firmware image merely because its hardware looks similar.**
- The owner unlocked the bootloader and updated the phone using Motorola
  Software Fix to exact stock build **W1UIS36H.39-25-8**. The kernel reports
  `6.1.141-android14-11-gd77c4cd65aed-ab14680598`. The last connected
  checks on 2026-10-01 showed slot `_a`, unlocked bootloader, stock Android
  boot completion, and stock root `vbmeta` digest
  `68af36bb4575ddc46bd708239df57cd1f360d504fa35f2731476f222ab49d036`.
- The owner said they would back up before destructive testing. Confirm that
  a **current** backup exists before any first ROM installation or data wipe.
  The owner does not require `/data` decryption in custom recovery.
- The phone is **not connected now** (`adb devices` was empty on 2026-10-03).
  Do not infer its current screen or slot solely from the old reports. Do not
  share the device serial, IMEI, or private logs in public issues.

## Workspace map

| Path | Purpose |
| --- | --- |
| `ROADMAP.md` | Progress tracker; read it, but this handoff has the newer interrupted-build audit. |
| `research/` | Device facts, build report, recovery tests, fastbootd assessment, VINTF, SELinux, AVB, firmware inventories. |
| `sources.lock.json` | Pinned crDroid manifest, Motorola kernel/module, and MediaTek source revisions; its `phone_stock_build` is a **historical** pre-update value. |
| `local_manifests/vienna-sources.xml` | Pinned local manifest for the research source trees. |
| `device/motorola/vienna/` | Top-level source copy, **currently behind** the active device tree. |
| `crdroid/device/motorola/vienna/` | Active device tree in the ignored 1,184-project crDroid checkout; it has the latest recovery, AVB, and super changes. |
| `crdroid/vendor/motorola/vienna/` | Generated local vendor imports; proprietary files are ignored. |
| `stock-firmware/` | Ignored exact-model Motorola firmware ZIP, extracted boot images, super, logical images, and extracted files. |
| `recovery-artifacts/` | Failed experimental recovery images and restore notes. None is a usable recovery. |
| `install-artifacts/` | Host-only experimental AVB image and warning. Not an install package. |
| `tools/` | Build, stock-image staging, recovery assembly, AVB, and research helpers. |
| `patches/` | Local source patches (one per repo and topic) to reapply with `git -C <repo> apply` after syncing Android source. |

The firmware ZIP is
`stock-firmware/XT2409-1_VIENNA_RETEU_16_W1UIS36H.39-25-8_CFC.xml.zip`,
6,903,313,944 bytes, SHA-256
`f38e07b14b1c984c44b736d7608d06be4e352b347e2ae554a470b728e81236dd`.
The exact stock `vendor_boot.img` is
`crdroid/device/motorola/vienna/prebuilts/vendor_boot.img`, SHA-256
`a3876fb1d1aee3c62ba78037f67c207fa65cc50b607259559e6ef37737c7071f`.
Stock root `vbmeta.img` is `stock-firmware/extracted/vbmeta.img`, SHA-256
`c0229c6cf41e3658366120c9e72ba8c497227cc85d1fbc9cdbcfa60b50ccec42`.
`tools/stage_stock_images.py` checksums the pinned inputs when staging them.
Do not commit or publish Motorola/MediaTek proprietary binaries.

## Source and host build work already completed

- crDroid manifest branch `16.0`, observed commit
  `7aeb04f96139aca17be68cb5ad91b3204136bf52`; resolved checkout manifest
  is `research/crdroid-12.12-resolved.xml`. Motorola kernel and device-module
  source tags are `MMI-W1UIS36H.39-25-8`; exact commits are in
  `sources.lock.json`. Complete kernel module rebuilding is **not established**
  because public source lacks referenced MediaTek modules. The current ROM
  prototype uses exact stock kernel, boot images, vendor, and module images.
- `bash tools/build_systemimage.sh` runs `lunch lineage_vienna bp4a userdebug`
  and builds requested targets, defaulting to `systemimage systemextimage
  productimage`. It writes `crdroid/out/build-systemimage.log` and, on a normal
  script exit, `crdroid/out/build-systemimage.exit-code`. An interrupted build
  can leave **no exit-code file**. The host filesystem had about 241 GB free
  on 2026-10-03.
- System, system_ext, and product EROFS images built and passed host integrity
  checks. A previous complete target-files package passed ZIP and AVB checks.
  Its APEX-aware VINTF check passed for `dns`, first API level 34, packaged
  kernel config, and VNDK 31/33/34. Stock vendor SELinux policy combined with
  built platform/system_ext/product CIL in a **host** check. None of these
  proves runtime boot, SELinux labels, radio, camera, or OTA behavior. See
  `research/prototype-image-build.md`, `research/sepolicy-stock-vendor-compat.json`,
  and `crdroid/out/vintf-targetfiles-success.log`.
- The initial proprietary list has 49 exact-stock entries; the active vendor
  tree includes MediaTek telephony/IMS blobs, four bootclasspath JARs, and
  their generated text build rules. APK signing and native link fixes are
  documented in `README.md`. It is a prototype, not a complete extraction.
- After source resync, inspect/reapply
  `patches/frameworks-base-systemui-nullable-album-art.patch` and
  `patches/build-make-prebuilt-target-files.patch`. The arm64 Chromium WebView
  prebuilt must be a real LFS object; `tools/fetch_lfs_object.py` verifies it.

## Artifact state that matters most

| Artifact | State |
| --- | --- |
| `crdroid/out/target/product/vienna/lineage_vienna-ota.zip` | **Old** complete A/B OTA from 2026-09-30, 2,406,993,794 bytes, SHA-256 `0639bbe5c0f2d40ba5739862e9538a4daa3b94467b5098ef53d8628a021f1288`. It predates the AVB/super corrections, is unbooted and test-key signed. **Do not install.** |
| `crdroid/out/target/product/vienna/obj/PACKAGING/target_files_intermediates/lineage_vienna-target_files.zip` | **0 bytes** after the 2026-10-01 packaging run was interrupted. No exit-code file exists. **Rebuild it.** |
| `.../lineage_vienna-target_files/IMAGES/` | Expanded intermediates from the interrupted run exist. They are useful for inspection, not a complete install package. |
| Expanded `IMAGES/vbmeta.img` and `vbmeta_system.img` | Inspected 2026-10-03: both rollback index **25**, both contain exact stock `KERN_PROT_META` and `HAB_META` properties, root flags 0 and a test-key `vbmeta_system` chain at rollback location 2. |
| Expanded `IMAGES/super_empty.img` | Inspected 2026-10-03: virtual A/B groups `main_a` and `main_b`, each max 23,083,352,064 bytes, matching the phone's read-only `lpdump`. |
| `install-artifacts/vbmeta-stockboot-crdroid-host-prototype.img` | 8,192-byte **host-only** root metadata, SHA-256 `8dc6d687d5c6d9e2e72a5beff41887da6ec9e5fd3eba1e36348f146c4ed2bc43`. `tools/make_stockboot_crdroid_vbmeta.py` generated it from the expanded intermediate and stock root; regenerate after the package rebuild. **Do not flash.** |

The old OTA's root `vbmeta` used rollback index **0** and lacked Motorola's
`KERN_PROT_META`/`HAB_META`; its super metadata used different group names.
The active `BoardConfig.mk` now specifies rollback index 25, both boot
properties for root and child metadata, and exact `main` group names/size.
The corrected expanded images show those changes took effect, but ZIP
packaging and OTA regeneration did **not** finish. On an unlocked device AVB
verification errors may be tolerated; the old index 0 is a risk to eliminate,
not a proven cause of any boot failure.

The stock boot, init_boot, DTBO and vendor_boot **unpadded payloads** matched
their old generated images byte-for-byte; Android regenerated their AVB
footers, so full-file hashes differ. For a first-boot path that leaves stock
boot files untouched, the host-only vbmeta tool starts from stock root
descriptors and changes only product, product properties, and the child key.
On 2026-10-03 its generated image passed a strict AOSP `avbtool verify_image`
check with the expected child key at rollback location 2, the built
system/system_ext/product hashtrees, and exact stock boot/vendor/module images.
**This is host cryptographic agreement only, not a boot test.**

## Recovery tests and stock restoration

The Edge 50 Neo has no standalone recovery partition; recovery is a fragment
in `vendor_boot`. An unofficial OrangeFox image under `recovery-artifacts/`
targets kernel `6.1.99`, not this phone's `6.1.141`, and is unsuitable.

The `lineage_vienna_recovery` target built successfully (`crdroid/out-recovery/
build-recovery.exit-code` is `0`). Three exact-firmware `vendor_boot` recovery
variants were tried on slot A: a full built fragment, a smaller stock-based
fragment, and a stock-based fragment with ABI-compatible libc++/Binder
libraries. **All three failed to boot recovery**: no custom recovery ADB,
with MediaTek preloader cycles/boot logo or black screen. Matching test-key
root vbmeta did not solve it. A test-key root vbmeta with stock descriptors
*alone* did boot stock Android, so the unlocked bootloader did not reject the
test key outright. Host ELF analysis found 14 unresolved symbols in the first
stock-based image; adding matching libraries removed those missing symbols,
but the revised image still failed. No definitive remaining cause was found.
Saved Android `SYSTEM_LAST_KMSG` entries were from later stock recovery boots,
not the failed custom boots. See `research/custom-recovery-assessment.md` and
`recovery-artifacts/README.md`.

After every test, stock images were restored and Android booted. For slot A,
the known restore order from bootloader fastboot is:

```sh
fastboot flash vbmeta_a stock-firmware/extracted/vbmeta.img
fastboot flash vendor_boot_a crdroid/device/motorola/vienna/prebuilts/vendor_boot.img
fastboot reboot
```

Flash stock **vbmeta first**: fastboot returned `Preflash validation failed`
when stock vendor_boot was flashed while a matching test-key vbmeta remained
installed; it accepted stock vendor_boot after restoring stock vbmeta. If the
phone lands at stock recovery's “No command” screen, `adb reboot` returned it
to Android in a prior test. Confirm device identity and active slot before any
restore. The phone was last confirmed back in Android on 2026-10-01, with
`sys.boot_completed=1` and the original Motorola vbmeta digest above.

## Fastbootd as the alternate installation route

Stock Motorola userspace fastboot was tested **read-only**: `adb reboot
fastboot` entered it; `fastboot getvar is-userspace` returned `yes`,
`current-slot` returned `a`, `is-logical:system_a` returned `yes`, and
`partition-size:super` returned `0x560000000` (23,085,449,216 bytes).
`fastboot reboot` returned the phone to Android, where ADB confirmed boot
completion. On-device `lpdump` showed `main_a`/`main_b`, the exact group sizes
above, and no pending virtual A/B snapshot update. See
`research/fastbootd-assessment.md`. [AOSP fastbootd documentation](https://source.android.com/docs/core/architecture/bootloader/fastbootd)
explains why userspace fastboot is relevant for logical partitions.

No ROM partition was flashed by fastbootd. A possible first-boot route is to
prepare exact stock boot/vendor images plus built system/system_ext/product
and matching signed vbmeta, then review a slot B flash plan. Do **not** run
the old `fastboot update` ZIP as-is: its generated `fastboot-info.txt` flashes
boot images and updates super metadata, while the current package is
incomplete and unbooted. A/B slots share `/data`; slot A is not a complete
data rollback plan. Prepare backups, exact slot commands, a data strategy,
and stock recovery steps before any first ROM flash.

## Source tree divergence to resolve before rebuilding

`crdroid/` is ignored by the top-level `.gitignore`; the active tree contains
changes that the top-level `device/motorola/vienna/` copy lacks:

- Active `BoardConfig.mk` has the separate recovery target settings, exact
  `main` super group, rollback index 25, and Motorola AVB properties.
- Active `AndroidProducts.mk` lists `lineage_vienna_recovery.mk`; that product
  file and `recovery/root/init.recovery.mt6878.rc` exist only in the active
  tree.
- The top-level source copy has `overlay/frameworks/base/core/res/res/values/config.xml`,
  while that overlay file is missing from the active tree despite `device.mk`
  referencing it. Review and synchronize it before a clean rebuild.
- The two device-tree README copies are stale in different ways; prefer this
  handoff and the dated research notes. The root `README.md` also still says
  the phone runs `W1UIS36H.39-17-8`; that is historical.

Keep the top-level device source and active checkout synchronized deliberately
before publishing or resyncing. The current expanded images predate any such
source synchronization and will need a fresh build if inputs change.

## Next actions for Claude

1. Audit/synchronize the device-tree copies above. Confirm pinned stock
   inputs with `tools/stage_stock_images.py` and inspect local patches before
   any source resync. Avoid silently overwriting active bring-up work.
2. Rebuild the corrected target-files package from this workspace:

   ```sh
   bash tools/build_systemimage.sh target-files-package
   cat crdroid/out/build-systemimage.exit-code
   unzip -tq crdroid/out/target/product/vienna/obj/PACKAGING/target_files_intermediates/lineage_vienna-target_files.zip
   ```

   The previous run reached `add_img_to_target_files.py: done` and began
   packaging, then stopped; no builder process was running on 2026-10-03.
   If a sandbox blocks Soong's local socket with `setsockopt: operation not
   permitted`, run the build with the required elevated execution approval.
   Verify ZIP size, generated root/child rollback 25 and Motorola properties,
   `main_a`/`main_b` group sizes, AVB chain, and APEX-aware VINTF again.
3. Only after target-files validation, rebuild `otapackage`, verify its ZIP,
   metadata, payload hashes, and record a **new** SHA-256. The 2026-09-30 OTA
   must not be reported as the corrected one.
4. Regenerate `install-artifacts/vbmeta-stockboot-crdroid-host-prototype.img`
   with `tools/make_stockboot_crdroid_vbmeta.py` from the validated package.
   Strictly verify its child chain and all partition descriptors against the
   actual images. The existing image demonstrates the method but must not be
   treated as a release artifact.
5. Prepare and review an installation method through stock fastbootd that
   preserves a return path to exact stock firmware. Decide which slot to use,
   how to handle shared `/data`, and which stock boot/vendor partitions must
   be present on that slot. Obtain a current phone/backup check before any
   first ROM flash. The custom recovery path still needs a separate root
   cause and is **not** a prerequisite if fastbootd installation works.
6. After a successful first boot, inspect enforcing SELinux, encryption,
   cellular and emergency calls, Wi-Fi, Bluetooth, camera, audio, GPS, NFC,
   fingerprint, sensors, and OTA. A host build or VINTF pass cannot replace
   these device tests. There is no reliable completion date yet.

Do not claim a flashable/bootable port until a controlled crDroid boot and
return-to-stock route have actually been tested on this XT2409-1.

## Session update 2026-10-03 (evening) — READ THIS FIRST

Supersedes conflicting statements above.

- **Custom recovery works** (Lineage recovery from the crDroid tree):
  `recovery-artifacts/working/` (v1) with root cause and rebuild notes in its
  README. Known issue: "Reboot system now" does not reboot (selection never
  returns from the menu; `adb reboot` works). Recovery source carries temporary
  `vienna_dbg()` kmsg markers and an `unsetenv("LD_LIBRARY_PATH")` fix in
  `crdroid/bootable/recovery` (uncommitted).
- **Device-tree copies synchronized** (overlay restored to the active tree).
- **Target-files rebuilt and validated** (rollback 25, Motorola AVB props,
  `main_a`/`main_b`). crDroid system/system_ext/product were flashed to
  **slot A** through fastbootd; `fastboot -w` was run (owner's data wiped with
  consent). Root vbmeta: `tools/make_stockboot_crdroid_vbmeta.py` output fed to
  `tools/make_matching_recovery_vbmeta.py` (stock boot chain + crDroid product
  + recovery vendor_boot hash); strict `avbtool verify_image` passed.
- **First crDroid boot failed** at 2.7 s: second-stage init aborted with
  `Duplicate prefix match detected for 'persist.vendor.pco5.radio.ctrl'`
  (property contexts). Cross-partition check found two conflicts between
  crDroid system_ext and stock vendor: `persist.vendor.pco5.radio.ctrl` and
  `vendor.camera.aux.packagelist`. Fixed by commenting them out on the
  crDroid side: `patches/device-mediatek-sepolicy_vndr-drop-pco5-prop.patch`,
  `patches/device-lineage-sepolicy-drop-camera-aux-prop.patch`.
- **Slot B now holds full stock W1UIS36H.39-25-8** (all 25 slotted images from
  the flashfile plus stock logical partitions) as a crash-log reader: after
  `fastboot set_active b; fastboot set_active a` (resets slot A to 7 tries,
  not successful), a crDroid bootloop falls back to slot B automatically
  (warm reboot), and `adb shell dumpsys dropbox --print SYSTEM_LAST_KMSG`
  there shows crDroid's last boot. Entering the bootloader menu clears pstore.
  Flashing stock `vendor_boot_b` needed a temporary stock `vbmeta_a`
  ("Preflash validation" checks the active slot's vbmeta).
- Logs: `stock-info/crdroid-bootlogs/` (ignored; may contain identifiers).

### 2026-10-03 late: FIRST crDroid BOOT on slot A

After the two property_contexts patches, `system_ext_a` + `vbmeta_system_a`
were reflashed (vbmeta_system verified against system/system_ext with avbtool;
same test key and rollback index 25 as the root chain descriptor), then
`fastboot -w`, `set_active b; set_active a`, and reboot. crDroid reached the
setup wizard (ADB up ~55 s, then USB switched to MTP). Slot A still uses the
permissive debug recovery `perm3` in `vendor_boot_a` — replace it with a clean
recovery before calling this a release. Hardware tests not done yet.

### 2026-10-04: telephony, IMS and microG

- **Root vbmeta carries the product hashtree digest.** After any product.img
  rebuild, run `tools/update_root_vbmeta_product.py --root <current vbmeta_a>
  --product crdroid/out/target/product/vienna/product.img --out <new>` and
  flash the result to `vbmeta_a`. Otherwise first-stage init hangs on the
  Motorola logo with no USB at all. Current slot A root vbmeta:
  `recovery-artifacts/bisect/perm3-vbmeta-crdroid-microg.img` (perm3 debug
  recovery + microG product).
- `ro.telephony.default_network=26,26` added (default was mode 0, 2G/3G only).
  It only applies to new SIM records; on an already-set-up device use
  `cmd phone set-allowed-network-types-for-users -s <slot> 11001101001110000111`.
- Stock `ImsService` crashed with NoClassDefFoundError TelephonyMetrics. Fixes
  in crdroid source (not yet saved as patches):
  `frameworks/opt/telephony/.../metrics/TelephonyMetrics.java` (no-op stub) and
  hidden compatibility constructors in `ImsReasonInfo` (4 args) and
  `ImsExternalCallState` (8 args) in frameworks/base. After that, the service
  runs with no crashes.
- IMS binding: Android 16 reads `config_ims_mmtel_package` from TeleService,
  not framework-res, so the stock MTK framework overlay no longer applies. The
  device overlay now sets it to `com.mediatek.ims`, enables
  `config_device_{volte,vt,wfc_ims}_available`, and adds a CarrierConfig
  `vendor.xml` with stock VoLTE/VoWiFi values for 216-01 (Yettel) and 216-30
  (Telekom), taken from stock CarrierSettings `s21601.pb`/`s21630.pb`. Testing
  with `cmd phone ims set-ims-service -d -f 0,1 com.mediatek.ims` showed
  MMTEL READY on both slots.
- microG 0.3.17 (GmsCore + Companion) bundled as product priv-apps from
  `device/motorola/vienna/microg/`. crDroid already spoofs signatures for these
  packages. microG is the network location provider.
- SELinux denials seen are harmless lookups of absent Lineage HALs and
  default_prop reads. vtservice spams ccci denials (video telephony).

## 2026-10-04: Bluetooth and fingerprint

- Bluetooth paired but never connected: only LE Audio profiles started because
  the classic `bluetooth.profile.*.enabled` props live in stock
  `system/build.prop`, which crDroid replaces. They are now in `device.mk`
  `PRODUCT_SYSTEM_PROPERTIES` (A2DP, HFP AG, AVRCP TG, HID, PAN, PBAP, MAP, OPP,
  BAS, ASHA, GATT), together with `wifi.*interface` and
  `persist.vendor.wfc.sys_wfc_support=1`.
- Fingerprint: Egis optical UDFPS (`ets_hal`, rbs AIDL HAL). Touch, onPointerDown
  and onUiReady all work; enrollment failed with `SCRATCH_DETECTED` because the
  image was too dark. It succeeds with the brightness slider at max. Stock
  boosts via the Moto panel HAL (`IDisplayPanel` setParam `HIGH_BRIGHT_FOD`)
  from its own system_server and SystemUI, which crDroid lacks.
- Fix (local HBM like stock): new SystemUI `UdfpsMotoPanelHbm` (enabled by
  `config_udfpsMotoPanelHbm` in the device SystemUI overlay). On finger down it
  adds a black dim layer with a hole over the sensor, waits for it to reach the
  screen, then calls `IDisplayPanel/default` transaction 5 `setMode(int)` with
  4 = HIGH_BRIGHT_FOD. On finger up it sets 0 = NORMAL and removes the layer.
  Modes come from `displaypanel.default.so`: 0 NORMAL, 1 POWER_SAVING,
  2 NATIVE, 3 HIGH_BRIGHT, 4 HIGH_BRIGHT_FOD. SystemUI (`platform_app`) is in
  `hal_moto_panel_client`; shell is not. The dim alpha uses
  `config_udfpsMotoPanelBrightnessNits` plus `config_udfpsMotoPanelHbmNits`
  (1600, a guess: tune it if the rest of the screen visibly changes during a
  scan). A fallback `config_udfpsBoostBrightness` (full-screen temporary max
  brightness) also exists. The egis HAL's own `set_hbm` uses the HIDL panel
  service, which this firmware lacks. The source is in `frameworks/base`
  (uncommitted) and must be saved as a patch.

## 2026-10-04: Yettel SIM drops

- Yettel (216-01) LTE attach was rejected with EMM cause 19 (ESM failure),
  then the SIM fell back to GSM and cycled out of service. The Lineage APNs
  (`vendor/apn/HU.xml`) had only old Pannon/Telenor IPv4 entries and no IMS
  APN. They are replaced with the stock Moto entries: `online` (IPV6,
  default,supl,xcap), `mms`, and `ims` (IPV6). The change is in `vendor/apn`
  (uncommitted) and must be saved as a patch.
- TelephonyProvider did not reload the APN DB after flashing. Run
  `adb shell content delete --uri content://telephony/carriers/restore` (or
  Settings APN "Reset to default"), then toggle airplane mode.
- Result: both SIMs on LTE with IMS (VoLTE) registered.

## Source patches (2026-10-04)

All crDroid source edits are saved in `patches/` and verified against the tree.
Apply with `git -C crdroid/<repo> apply patches/<file>`:

| Patch | Repo |
|---|---|
| `build-make-prebuilt-target-files.patch` | `build/make` |
| `device-lineage-sepolicy-drop-camera-aux-prop.patch` | `device/lineage/sepolicy` |
| `device-mediatek-sepolicy_vndr-drop-pco5-prop.patch` | `device/mediatek/sepolicy_vndr` |
| `frameworks-base-systemui-nullable-album-art.patch` | `frameworks/base` |
| `frameworks-base-ims-mtk-constructors.patch` | `frameworks/base` |
| `frameworks-base-systemui-udfps-moto-panel-hbm.patch` | `frameworks/base` |
| `frameworks-opt-telephony-telephonymetrics-stub.patch` | `frameworks/opt/telephony` |
| `vendor-apn-yettel-stock-apns.patch` | `vendor/apn` |
| `bootable-recovery-vienna-fixes.patch` | `bootable/recovery` |

## 2026-10-04: Bluetooth audio

- Headphones connected but played silence. A2DP hardware offload (AAC) negotiated
  fine: vendor offload start OK, MTK `MtkBTAudioProviderA2dpHW` streamStarted
  SUCCESS, DSP running. But no audio reached the headset, with
  `BTAudioSessionAidl ... has NO port state observer`.
- Developer option "Disable Bluetooth A2DP hardware offload" fixes it (software
  encoding through stock `audio_policy_configuration_a2dp_offload_disabled.xml`).
  Now the default via `PRODUCT_PRODUCT_PROPERTIES +=
  persist.bluetooth.a2dp_offload.disabled=true` (product props override
  vendor's `false`). Not yet rebuilt or flashed; the owner's phone already has
  the persisted value.

## 2026-10-04: owner test results (crDroid on slot A)

Working: boot, both SIMs on LTE with VoLTE (Yettel 216-01, Telekom 216-30),
voice calls, camera, GPS, microG network location, fingerprint (local HBM),
face unlock, Bluetooth pairing and A2DP audio (offload disabled).
Not yet tested: Wi-Fi calling, NFC, charging and battery life, video calls.
Open: the recovery on the device is the permissive debug `perm3`
(replace it with a clean one); the next build should include
`persist.bluetooth.a2dp_offload.disabled=true` from device.mk.

## 2026-10-04: clean Lineage recovery

- `perm3` was `v1` plus debug-only changes: permissive `adbd`/`recovery`/
  `shell`/`su` domains, pstore exposed in `init.rc`, `vienna_dbg` kmsg markers
  and `androidboot.init_fatal_reboot_target=recovery` on the kernel command line.
- The clean recovery is `v1`'s layout (stock enforcing sepolicy, stock
  cmdline, unchanged normal ramdisk), generated reproducibly by
  `tools/make_recovery_fragment.py`. See `recovery-artifacts/clean/README.md`.
- "Reboot does nothing" root cause: the stock policy denies the recovery a
  `NETLINK_KOBJECT_UEVENT` socket ("Vold: Unable to create uevent socket:
  Permission denied"), so `NetlinkManager::start()` fails. On every reboot or
  power-off, `VolumeManager::stop()` then called `mHandler->stop()` on an
  uninitialized/null handler, causing SIGSEGV, and init restarted the recovery
  (USB never dropped). Fixed in `bootable/recovery`, saved as
  `patches/bootable-recovery-vienna-fixes.patch` (also keeps the
  `LD_LIBRARY_PATH` unset for sideload).
- Debug method that worked: under enforcing policy, reboot from recovery to
  crDroid with `adb reboot`, then `adb shell cat /sys/fs/pstore/console-ramoops-0`
  (shell is in group `log`). Kernel rate limiting hid the important lines;
  `--extra-cmdline printk.devkmsg=on` on the vendor_boot fixes that (init
  cannot write the printk sysctls under the stock policy).
- Verified on the phone: menu works, "Advanced → Reboot to bootloader" and
  "Reboot system now" work, crDroid boots. Current slot A: `vendor_boot_a` =
  `recovery-artifacts/clean/clean-vendor_boot.img`, `vbmeta_a` =
  `recovery-artifacts/clean/clean-vbmeta-crdroid.img` (perm3-apn root with
  the clean vendor_boot digest).
