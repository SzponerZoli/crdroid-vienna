# Connected test phone state (2026-09-30)

Read-only `adb shell getprop` after the owner connected the Motorola Edge 50
Neo. The phone was not rebooted, flashed, or modified. Serial number is omitted.

| Property | Value |
| --- | --- |
| `ro.product.model` | `motorola edge 50 neo` |
| `ro.product.device` | `vienna` |
| `ro.boot.hardware.sku` | `XT2409-1` |
| `ro.boot.product.hardware.sku` | `dns` |
| `ro.boot.flash.locked` | `0` |
| `ro.boot.verifiedbootstate` | `orange` |
| `ro.boot.slot_suffix` | `_a` |
| `ro.build.version.release` / SDK | `16` / `36` |
| `ro.product.first_api_level` | `34` |
| System build | `W1UIS36H.39-17-8` |
| Vendor build | `W1UIS36H.39-17-8` |

## Recheck after Motorola update (2026-10-01)

Read-only ADB confirms the connected XT2409-1 now reports system build
`W1UIS36H.39-25-8` and vendor fingerprint
`motorola/vienna_g_vext/vienna:14/W1UIS36H.39-25-8/a587a:user/release-keys`.
The kernel remains `6.1.141-android14-11-gd77c4cd65aed-ab14680598`.
The active slot is `_a`; `ro.boot.flash.locked=0` and verified boot state is
`orange`. No prototype image has been boot-tested or installed.
