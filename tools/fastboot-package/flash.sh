#!/usr/bin/env bash
# Flash crDroid for Motorola Edge 50 Neo (XT2409-1, vienna) with fastboot.
#
# Requirements: unlocked bootloader; the ACTIVE slot runs stock firmware
# W1UIS36H.39-25-8 (crDroid reuses its boot, init_boot, dtbo and vendor
# images); the phone is in bootloader (fastboot) mode.
#
# Usage: ./flash.sh [--wipe]
#   --wipe   format userdata (required when coming from stock or another ROM)
set -euo pipefail
cd "$(dirname "$0")"

wipe=0
case "${1:-}" in
    --wipe) wipe=1 ;;
    "") ;;
    *) echo "usage: $0 [--wipe]"; exit 2 ;;
esac

command -v fastboot >/dev/null || { echo "fastboot not found in PATH"; exit 1; }
if command -v sha256sum >/dev/null; then check="sha256sum -c --quiet"; else check="shasum -a 256 -c --quiet"; fi
$check SHA256SUMS || { echo "Image checksum mismatch, aborting."; exit 1; }

echo "Waiting for the phone in bootloader mode..."
fastboot devices | grep -q . || { echo "No fastboot device. Reboot to bootloader first."; exit 1; }
if [ "$(fastboot getvar is-userspace 2>&1 | awk '/is-userspace/{print $2}')" = "yes" ]; then
    echo "The phone is in fastbootd. Choose 'Reboot to bootloader' first."; exit 1
fi
slot=$(fastboot getvar current-slot 2>&1 | awk '/current-slot/{print $2}')
echo "Active slot: ${slot:-unknown}"

echo
echo "This flashes crDroid to the active slot."
[ "$wipe" = 1 ] && echo "USERDATA WILL BE ERASED."
read -r -p "Type 'yes' to continue: " answer
[ "$answer" = "yes" ] || { echo "Aborted."; exit 1; }

# The bootloader only accepts vendor_boot when it matches the active slot's
# vbmeta, so vbmeta goes first.
fastboot flash vbmeta images/vbmeta.img
fastboot flash vendor_boot images/vendor_boot.img

fastboot reboot fastboot
for part in system system_ext product vbmeta_system; do
    fastboot flash "$part" "images/$part.img"
done
if [ "$wipe" = 1 ]; then
    fastboot -w
fi
fastboot reboot
echo "Done. The first boot takes about a minute."
