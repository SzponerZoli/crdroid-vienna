crDroid 12 (Android 16) for Motorola Edge 50 Neo XT2409-1 (vienna)
Unofficial build, fastboot package. https://github.com/SzponerZoli/crdroid-vienna

USE AT YOUR OWN RISK. Flashing can erase your data or leave the phone
unbootable. Provided "as is", without warranty (Apache License 2.0, sections
7 and 8). Not affiliated with Motorola, MediaTek or the crDroid team.

REQUIREMENTS
- Motorola Edge 50 Neo XT2409-1 (RETEU tested) with an unlocked bootloader.
- The ACTIVE slot must run stock firmware W1UIS36H.39-25-8. This package
  replaces only system, system_ext, product, vbmeta_system, vendor_boot
  (Lineage recovery) and vbmeta; it reuses that slot's stock boot, init_boot,
  dtbo and vendor images. Other firmware versions will not boot.
- Android platform-tools (fastboot) on your computer.
- A backup, and the stock firmware package for your exact model at hand.

INSTALL
1. Boot the phone to the bootloader (power off, then hold Power + Volume Down).
2. Linux/macOS:  ./flash.sh --wipe        Windows:  flash.bat --wipe
   Use --wipe when coming from stock or another ROM (formats userdata).
   Updating an existing install of this build: run without --wipe.
3. The phone reboots into crDroid; the first boot takes about a minute.

The script checks the image checksums (SHA256SUMS) before flashing.

INCLUDED
microG (GmsCore, Companion), Lineage recovery in vendor_boot. Known issues
and source code: see the GitHub repository.
