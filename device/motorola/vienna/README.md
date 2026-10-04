# crDroid vienna device tree

> **Current status:** this tree builds a crDroid that boots and runs daily on
> XT2409-1 RETEU (see the [top-level README](../../../README.md)). The notes
> below describe the original bring-up design and are kept for reference;
> statements that runtime behavior is unverified predate the first boot.

This is the product target for **Motorola Edge 50 Neo XT2409-1 RETEU**.
It uses crDroid 12 / Android 16 system components with exact-model stock
`W1UIS36H.39-25-8` boot, vendor, kernel module, and DTBO images. The images
must be staged under `prebuilts/` using `tools/stage_stock_images.py` before a
build. No Motorola binary is tracked in this source directory.

This target is for build bring-up. Its VINTF, init, framework blob, AVB,
recovery, and SELinux integration is incomplete. A successful `lunch` or image
build does not prove that it boots or is safe to flash. The first three
prototype images now build successfully. The phone was updated to the same
`W1UIS36H.39-25-8` build these prebuilts use. Its bootloader is unlocked.

In particular, the stock `system_ext` image contains `ImsService.apk`,
`MtkTelephonyAssist.apk`, and MediaTek and Motorola telephony framework JARs.
The 49-entry `proprietary-files.txt` is an initial exact-model extraction list;
every path exists in the extracted stock firmware. All 49 entries have been
extracted into the ignored `crdroid/vendor/motorola/vienna/` tree. The initial
42 copied files match stock except for the `libsink-mtk.so` rename and matching
`libimsma.so` ELF reference fix. Seven more files cover the stock audio,
telephony early-read, and thermal services. `device.mk` inherits the generated
vendor rules;
the build integration passed, but runtime behavior remains unverified. In particular,
APK signing, framework class paths, SELinux, and runtime
behavior still need work. Calls, including emergency calls, need explicit
verification after integration.

The stock audio parameter parser links to audio AIDL core V3. The current
source audio-types library pulls V4 into Soong's dependency graph, so the
parser uses `DISABLE_DEPS` in the extraction list and `device.mk` installs its
runtime libraries directly. This only resolves the build graph; the binary's
loader and audio behavior still require on-device checks.

`BoardConfig.mk` includes the generic MediaTek policy and exact `system_ext`
labels for the stock `terservice` and `thermald` binaries. The static audit finds
64 vendor-referenced stock policy names absent from the generic source. A
focused source policy build passed, and a host split-policy compile with the
actual stock vendor CIL and 34.0 mapping passed. Service labels and runtime
policy behavior still need validation.

Five MediaTek IMS apps declare `android.uid.phone` and are configured to use
the crDroid platform key in the generated vendor rules. The other three APKs
retain stock signatures. This only addresses package installation requirements;
telephony behavior has not been tested.

`ImsService.apk` also requires the `moto-telephony` shared library. Its stock
JAR and library declaration from the `system` partition are in the list.
The four MediaTek framework JARs shown in stock `bootclasspath.pb` are marked
`BOOT_JAR` in `proprietary-files.txt`. The extractor declares them as
`PRODUCT_BOOT_JARS` and sets `use_generic_config` on their Soong imports;
the first image build completed; runtime behavior still needs validation.

The `overlay/` directory has the exact stock display cutout path and status
bar heights. `device.mk` includes it in the active checkout.

`recovery.fstab` is copied byte-for-byte from `system/etc/recovery.fstab` in
the second vendor ramdisk of the pinned `W1UIS36H.39-25-8` `vendor_boot.img`
(SHA-256 `60593cb44d2172a1c6793439cf6bad8e0d180ec0a0b28a1988af5889ff70bebf`).
Because this prototype retains the stock vendor boot image and does not build
a recovery image, Android's recovery build rules do not install this file.
`device.mk` explicitly enables A/B OTA package generation with
`PRODUCT_BUILD_GENERIC_OTA_PACKAGE`. The copied fstab remains an exact-model
reference for later recovery integration. Neither change proves that stock
recovery can install the resulting OTA.
