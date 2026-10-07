@echo off
rem Flash crDroid for Motorola Edge 50 Neo (XT2409-1, vienna) with fastboot.
rem Requirements: unlocked bootloader; the ACTIVE slot runs stock firmware
rem W1UIS36H.39-25-8; the phone is in bootloader (fastboot) mode.
rem Usage: flash.bat [--wipe]   (--wipe formats userdata; needed from stock)
setlocal
cd /d "%~dp0"

set WIPE=0
if "%~1"=="--wipe" set WIPE=1

where fastboot >nul 2>&1 || (echo fastboot not found in PATH & exit /b 1)

fastboot devices | findstr /r "." >nul || (echo No fastboot device. Reboot to bootloader first. & exit /b 1)
fastboot getvar is-userspace 2>&1 | findstr /c:"is-userspace: yes" >nul && (echo The phone is in fastbootd. Choose "Reboot to bootloader" first. & exit /b 1)

echo This flashes crDroid to the active slot.
if %WIPE%==1 echo USERDATA WILL BE ERASED.
set /p ANSWER=Type yes to continue:
if /i not "%ANSWER%"=="yes" (echo Aborted. & exit /b 1)

rem The bootloader only accepts vendor_boot when it matches the active slot's vbmeta.
fastboot flash vbmeta images\vbmeta.img || exit /b 1
fastboot flash vendor_boot images\vendor_boot.img || exit /b 1

fastboot reboot fastboot || exit /b 1
for %%P in (system system_ext product vbmeta_system) do (
    fastboot flash %%P images\%%P.img || exit /b 1
)
if %WIPE%==1 fastboot -w
fastboot reboot
echo Done. The first boot takes about a minute.
