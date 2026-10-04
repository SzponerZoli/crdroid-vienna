# Custom recovery assessment for XT2409-1 (`vienna`)

Checked 2026-10-01. No recovery partition exists on the connected phone.
`vendor_boot_a` and `vendor_boot_b` are present, with slot `_a` active. The
phone now reports Android 16 build `W1UIS36H.39-25-8` and kernel
`6.1.141-android14-11-gd77c4cd65aed-ab14680598`.

## Community OrangeFox image

The [ChimpanziCloud recovery tree](https://github.com/ChimpanziCloud/android_device_motorola_vienna)
publishes an [unofficial OrangeFox R12.0 image](https://github.com/ChimpanziCloud/android_device_motorola_vienna/releases/tag/33177401539)
for `vienna`. The 2026-08-28 `vendor_boot` image was downloaded to
`recovery-artifacts/OrangeFox-R12.0-Unofficial-vienna.img` and its SHA-256
matched the GitHub release asset digest:

`8ea0f6523deb43467c5dd1a38a1d804af515ff7474c6cfef25de21073a2e8077`

`unpack_bootimg` confirms a version 4 `VNDRBOOT` image, 67,108,864 bytes,
with normal and recovery ramdisk fragments. `avbtool info_image` reads a
`vendor_boot` hash footer signed by the recovery project's test key.

The image is **not suitable for installation on the connected phone**. A
display module extracted from its normal vendor ramdisk has `vermagic`
`6.1.99-android14-11-g1e00e55ba834`, while the phone runs kernel `6.1.141`.
The image's DTB is also different from the pinned XT2409-1
`W1UIS36H.39-25-8` stock DTB (326,635 versus 327,296 bytes). The image's
normal and recovery fragments occupy approximately 9.3 MiB and 43.3 MiB
compressed, respectively. The current stock normal fragment alone is about
29.0 MiB compressed, so simply replacing the normal fragment would exceed
the 64 MiB `vendor_boot` partition. Its recovery ramdisk would need to be
trimmed and rebuilt against matching kernel modules and DTB.

The public recovery tree's current prebuilt `mediatek-drm.ko` has yet another
`vermagic`, `6.1.68-android14-11-g7b7686d0c494`, so rebuilding it unchanged
would not fix the kernel mismatch.

## Exact-firmware recovery tests

The owner updated this XT2409-1 to `W1UIS36H.39-25-8`. A Lineage recovery
target built successfully against that firmware base. Two `vendor_boot`
variants were assembled with the exact stock normal ramdisk, DTB, and
bootconfig: one with the full built recovery fragment, and one with only the
Lineage recovery program, its needed libraries and resources added to the
stock recovery fragment. Both fit the 64 MiB partition and passed host AVB
hash checks. A no-change repack of Motorola's `vendor_boot` reproduced its
35,561,472-byte unpadded boot image exactly, so the image assembler preserves
the stock boot header and component layout.

Both variants failed slot A recovery boot tests: the phone showed a boot logo
or black screen, USB returned through MediaTek preloader, and ADB did not
connect to the custom recovery. The stock-based variant failed again with a
matching signed root `vbmeta` whose only descriptor change was its
`vendor_boot` hash and size. A separate test-key `vbmeta` with unchanged stock
descriptors successfully booted stock Android. This rules out an outright
bootloader rejection of the test key, but does not identify where the modified
`vendor_boot` fails. Android's saved `SYSTEM_LAST_KMSG` entries covered the
subsequent stock recovery boots, not the failed custom boots.

An ELF dependency check found 14 unresolved strong symbols in the first
stock-based recovery fragment. The new recovery program expected newer
libc++ and Binder APIs than Motorola's stock recovery libraries provide.
Adding the matching built `libc++.so`, `libbinder_ndk.so`, and `libbinder.so`
removed every unresolved strong symbol in its dependency closure. The
ABI-corrected image and its matching test-key `vbmeta` were host validated
and tested on slot A. Recovery still did not start: USB returned through
MediaTek preloader without recovery ADB. Both stock images were restored
again. This confirms the library mismatch was a real defect, while the
remaining boot failure has another cause. Do not flash any of these recovery
images as a usable recovery.

After the last test, stock `vbmeta_a` and `vendor_boot_a` were restored in that
order. Fastboot rejected stock `vendor_boot_a` with `Preflash validation failed`
until stock `vbmeta_a` had been restored during the prior test. The final
restoration also passed: Android booted and ADB confirmed `sys.boot_completed=1`, active slot
`_a`, firmware `W1UIS36H.39-25-8`, and Motorola's original root `vbmeta`
digest `68af36bb4575ddc46bd708239df57cd1f360d504fa35f2731476f222ab49d036`.

No working custom recovery is installed. Before another flash test, determine
why the modified `vendor_boot` fails before ADB starts, and keep a verified
route back to stock. The user's `/data` decryption preference does not remove
the kernel, display, touch, USB, or recovery boot requirements.

On 2026-10-01, the user checked Settings > System updates; it did not offer
`W1UIS36H.39-25-8`. `adb pull /dev/block/by-name/vendor_boot_a` returned
permission denied. In bootloader fastboot, `getvar max-fetch-size` returned
`not found`, so `fastboot fetch vendor_boot` failed without reading any data.
`fastboot reboot` then returned `OKAY`; after the user unlocked the screen,
ADB again reported the XT2409-1 running Android. AOSP documents `fastbootd` support for
fetching `vendor_boot`, but stock user builds normally cannot use its fetch
implementation. Motorola's
[Software Fix](https://help.motorola.com/hc/apps/service/rsa/58/en-us/CGT1908243440.html)
is an official fallback for obtaining exact-device firmware on Windows, but
its Rescue installation erases user data. The failed read attempts did not
flash or erase any partition. At the time of these checks, no Software Fix
Rescue installation had been performed.

Software Fix in the user's Windows VM subsequently identified the device as
XT2409-1 / RETEU and offered `W1UIS36H.39-25-8` for download. This confirms
Motorola's target build for this particular phone. Subsequently, on
2026-10-01, the owner completed the update. Read-only ADB now reports
`W1UIS36H.39-25-8` on the device, with the same `6.1.141` kernel and unlocked
bootloader. The firmware base is aligned; the custom recovery boot tests and
their results are described above.

## Bootloader analysis and bisect plan (2026-10-03)

Host reverse engineering of the exact-firmware `preloader.img` and `lk.img`
ruled out three bootloader-side causes for the failed recovery boots:

- **Ramdisk board IDs:** every fragment in stock and all failed images has an
  all-zero `board_id`, so LK's `board_id ... not matched` check is not it.
- **Ramdisk reservation:** the preloader's mblock table reserves `mb_ramdisk`
  at `0x66f00000` (the vendor_boot `ramdisk_addr`) with size `0x4000000`
  (64 MiB). LK copies the platform, recovery (recovery mode only) and generic
  ramdisks there and checks the total. The largest failed image needs about
  50 MiB, so it fits.
- **AVB heap:** LK loads `vendor_boot` through libavb's `loaded_partitions`
  into a fixed `0x8c00000` (140 MiB) AVB heap. The hash partitions total about
  53 MB for stock and 57 MB for the largest failed set.

Stock recovery's programs and libraries live in the **normal** vendor ramdisk
(`system/bin/recovery`, `adbd`, a dynamically linked `init`, and
`system/lib64/libc++.so` and `libbinder.so`). The recovery fragment is laid
over it. The ABI-compatible image replaced `libc++.so`, `libbinder.so`,
`libbinder_ndk.so`, `librecovery_ui*.so` and `recovery`. The replacements
lack 81 (`libc++`) and 792 (`libbinder`) stock exports, but no stock ELF in
the ramdisk imports any of them. Linkage alone therefore does not explain the
failure; runtime behavior is unproven.

The `lz4 -l -12` host tool reproduces Motorola's recovery fragment
byte-for-byte. Bisect images are in `recovery-artifacts/bisect/` (see its
README). Each failed test should be followed by booting **directly to
Android** (not stock recovery), then
`adb shell dumpsys dropbox --print SYSTEM_LAST_KMSG`, so the failed boot's
kernel log is not overwritten.

## Result: working recovery (2026-10-03)

The bisect found the cause. T1 (re-hashed stock fragment) and T2 (one added
file) booted stock recovery, so AVB/signing and fragment edits are fine.
Diagnostic images (T3–T8) showed init and ADB come up, but the Lineage
recovery's `/tmp/recovery.log` stayed empty: it crashed right after start
while using Motorola's stock libraries. T9 gave it a private crDroid library
set via `LD_LIBRARY_PATH`, but the dropbox `SYSTEM_LAST_KMSG` showed it
exiting with status 1 every 5 s: init's domain transition sets `AT_SECURE`,
so bionic ignored `LD_LIBRARY_PATH`. T10 added a static exec wrapper (no
transition) and the Lineage recovery UI appeared on the phone. The cleaned
image and full explanation are in `recovery-artifacts/working/README.md`.
