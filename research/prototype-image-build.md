# First prototype image build

On 2026-09-30, `bash tools/build_systemimage.sh` completed with exit code 0
for `lineage_vienna bp4a userdebug`. It built `systemimage`, `systemextimage`,
and `productimage` from the local crDroid 12 / Android 16 checkout. The build
log is `crdroid/out/build-systemimage.log` (ignored local output).

| Image | Bytes | SHA-256 |
| --- | ---: | --- |
| `crdroid/out/target/product/vienna/system.img` | 600535040 | `e1edfb576d1745024b8a498b6c043abc46bf48e2a9bf457108165210e1d0c0d3` |
| `crdroid/out/target/product/vienna/system_ext.img` | 580214784 | `4c108ebc0d6eccad5746bf3f6cc370d3a356cf82933e044385618df90c58a2cd` |
| `crdroid/out/target/product/vienna/product.img` | 381132800 | `a430e46b1c92ef25e27175f8a4e50043594a63f6833e4a82ada523b9ee086f25` |

All three are EROFS images. The built `fsck.erofs --extract` checked every
file in each image and returned 0. `avbtool info_image` reads a hashtree
footer from each image. These checks confirm host image integrity; they do
not establish VINTF compatibility, a valid boot chain, or device behavior.

The images use the prototype's Android test key, while exact-model stock AVB
uses Motorola's key. The owner subsequently updated the phone to the matching
stock firmware and unlocked its bootloader. These images remain **unbooted**.

## Target-files packaging

The target-files package completed on 2026-09-30 after staging the stock
prebuilt boot images and vendor partition build properties. Its archive is
`crdroid/out/target/product/vienna/obj/PACKAGING/target_files_intermediates/lineage_vienna-target_files.zip`
(3,939,925,465 bytes, SHA-256
`aee436e7f09db2ff00595888480233f018bb63dffc29a1250f6d6055b2c70d81`).
`unzip -tq` passed. Host `avbtool verify_image` passed for the root vbmeta,
the expected `vbmeta_system` chain at rollback location 2, and all included
partition hashes and hashtrees using the prototype test key. The package is
an intermediate build artifact, not an installable OTA zip. This validation
does not establish compatibility with Motorola's key or the attached phone.

## VINTF-adjusted rebuild

The next host build added the exact-stock framework and product VINTF
compatibility matrices and crDroid's VNDK 31, 33, and 34 APEXes. The Android
build generated matching `<vendor-ndk>` entries in the system_ext framework
manifest. A host `checkvintf --check-compat` run returned `COMPATIBLE` against
the extracted stock vendor and ODM VINTF files for `dns` and first API level
34. That run used an empty synthetic APEX information list, so it did not
cover APEX VINTF fragments.

The rebuilt target-files archive now includes all 58 stock vendor VINTF files,
all 8 stock ODM VINTF files, and `vintf_odm_manifest_skus=dns`. It is
`4,001,525,954` bytes, SHA-256
`a984123a1e31d93e21d886dd005042f8c0a81046c1f5ed09cf453c7dd610a086`.
`unzip -tq` passed. `avbtool verify_image --follow_chain_partitions`
passed for the root/child AVB chain and all 10 partition hashes and
hashtrees with the prototype test key. Android's hermetic
`check_target_files_vintf -v` then returned `compatible` with the packaged
APEXes activated by `apexd_host`, the `dns` SKU, first API level 34, and the
packaged kernel version/configuration. The verbose check log is retained
locally at `crdroid/out/vintf-targetfiles-success.log`.

## Candidate A/B OTA ZIP

`otapackage` completed on 2026-09-30 after enabling the A/B OTA target for
this product. The output is
`crdroid/out/target/product/vienna/lineage_vienna-ota.zip`,
2,406,993,794 bytes, SHA-256
`0639bbe5c0f2d40ba5739862e9538a4daa3b94467b5098ef53d8628a021f1288`.
`unzip -tq` passed. It contains a 2,406,986,307-byte `payload.bin`,
`payload_properties.txt`, APEX and care-map metadata, and the OTA certificate.
An independent stream over `payload.bin` matched its declared `FILE_SIZE`,
`FILE_HASH`, and `METADATA_HASH` in `payload_properties.txt`.
The OTA metadata says `ota-type=AB`, `pre-device=vienna`, post SDK 36, and
post security patch level 2026-09-01. Android's OTA generator ran the full
target-files VINTF check again and returned `compatible` for `dns`, API 34,
the packaged APEXes, and kernel requirements. Android signed the ZIP with
its development test key.

This is an **unbooted test candidate**. On 2026-10-01, the connected phone
updated to `W1UIS36H.39-25-8`, matching the package's stock boot/vendor/module
base. Subsequent review found that this archived candidate uses root AVB
rollback index 0 instead of stock 25, omits Motorola boot metadata properties,
and uses super group names different from the phone's. See the
[fastbootd assessment](fastbootd-assessment.md). Do not install this archived
candidate; a corrected package needs to be built and checked first.
