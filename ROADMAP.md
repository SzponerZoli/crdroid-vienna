# Roadmap

Target: Motorola Edge 50 Neo **XT2409-1 RETEU**, crDroid 12 / Android 16, on
stock firmware base `W1UIS36H.39-25-8`. Updated 2026-10-04. Details are in
the [bring-up log](docs/BRINGUP_LOG.md).

| Milestone | Status |
| --- | --- |
| Identify the device, pin sources and stock firmware | Done |
| Build crDroid system, system_ext and product against stock vendor | Done |
| Stock vendor SELinux, VINTF and VNDK compatibility (host checks) | Done |
| First boot on the phone | Done (2026-10-03) |
| Telephony: data and VoLTE registration on both SIMs | Done |
| Voice calls | Broken: calls drop as soon as they are answered (regression, under investigation) |
| Camera, GPS, fingerprint, face unlock, Bluetooth audio | Done |
| microG with signature spoofing | Done |
| Wi-Fi calling, video calls, NFC, battery and charging | Not tested |
| Boot with stock `vendor_boot` and generated root vbmeta (public install path) | Not tested |
| Lineage recovery for this firmware | Done (2026-10-04): enforcing stock policy; see `recovery-artifacts/clean/` |
| Re-enable A2DP hardware offload | Open: offload starts but plays silence |
| Flashable package (OTA ZIP or fastboot script) | Open |
| Wider device and firmware coverage (other XT2409 SKUs) | Open: needs testers |
