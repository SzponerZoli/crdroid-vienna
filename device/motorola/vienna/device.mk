# SPDX-License-Identifier: Apache-2.0

# First build prototype: keep the exact-model stock kernel and vendor images.
# They are staged separately from the verified Motorola firmware package.
$(call inherit-product, $(SRC_TARGET_DIR)/product/emulated_storage.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/virtual_ab_ota/launch_with_vendor_ramdisk.mk)

PRODUCT_USE_DYNAMIC_PARTITIONS := true
PRODUCT_SHIPPING_API_LEVEL := 34
PRODUCT_TARGET_VNDK_VERSION := 34
PRODUCT_EXTRA_VNDK_VERSIONS := 31 33 34
PRODUCT_VIRTUAL_AB_COMPRESSION_METHOD := lz4
# Stock vendor_boot supplies recovery, so no recovery image is built. Android
# otherwise hides its A/B OTA target when no built recovery fstab is present.
PRODUCT_BUILD_GENERIC_OTA_PACKAGE := true

# Match the exact stock vendor interface requirements. The VNDK snapshots
# above also provide the runtime APEXes named in the generated manifest.
DEVICE_FRAMEWORK_COMPATIBILITY_MATRIX_FILE += \
    device/motorola/vienna/vintf/compatibility_matrix.device.xml
DEVICE_PRODUCT_COMPATIBILITY_MATRIX_FILE += \
    device/motorola/vienna/vintf/compatibility_matrix.product.xml

# Exact stock display cutout and status bar dimensions for XT2409-1 RETEU.
PRODUCT_PACKAGE_OVERLAYS += device/motorola/vienna/overlay

PRODUCT_PACKAGES += \
    update_engine \
    update_engine_sideload \
    update_verifier

# Runtime DT_NEEDED libraries for the stock audio parameter parser. Its
# generated prebuilt omits Soong ELF dependencies because the current source
# audio-types module pulls AIDL core V4 while the stock binary uses V3.
PRODUCT_PACKAGES += \
    android.hardware.audio.core-V3-ndk \
    av-audio-types-aidl-ndk \
    libmedia_helper \
    libmediautils

# Default to NR/LTE/GSM/WCDMA on both SIMs; without this telephony falls back
# to mode 0 (WCDMA preferred) and never uses LTE or NR.
PRODUCT_SYSTEM_PROPERTIES += \
    ro.telephony.default_network=26,26

# Classic Bluetooth profiles, from stock system/build.prop. Without these only
# the LE Audio profiles start, so headphones pair but never connect.
PRODUCT_SYSTEM_PROPERTIES += \
    bluetooth.profile.a2dp.source.enabled=true \
    bluetooth.profile.asha.central.enabled=true \
    bluetooth.profile.avrcp.target.enabled=true \
    bluetooth.profile.bas.client.enabled=true \
    bluetooth.profile.gatt.enabled=true \
    bluetooth.profile.hfp.ag.enabled=true \
    bluetooth.profile.hid.host.enabled=true \
    bluetooth.profile.map.server.enabled=true \
    bluetooth.profile.opp.enabled=true \
    bluetooth.profile.pan.nap.enabled=true \
    bluetooth.profile.pan.panu.enabled=true \
    bluetooth.profile.pbap.server.enabled=true

# A2DP hardware offload starts cleanly but no audio reaches the headset with
# the AOSP Bluetooth stack; use software encoding (stock
# audio_policy_configuration_a2dp_offload_disabled.xml). Product props load
# after vendor, which sets this to false.
PRODUCT_PRODUCT_PROPERTIES += \
    persist.bluetooth.a2dp_offload.disabled=true

# Wi-Fi interface names and MTK WFC support flag, from stock system/build.prop.
PRODUCT_SYSTEM_PROPERTIES += \
    wifi.interface=wlan0 \
    wifi.tethering.interface=ap0 \
    wifi.direct.interface=p2p0 \
    persist.vendor.wfc.sys_wfc_support=1

# microG (official release APKs, see microg/README.md)
PRODUCT_PACKAGES += \
    GmsCore \
    FakeStore

# Stock system_ext telephony and IMS components extracted from the exact
# XT2409-1 RETEU firmware. The package list remains a bring-up candidate.
$(call inherit-product, vendor/motorola/vienna/vienna-vendor.mk)

# The four stock system_ext boot JARs are declared by the vendor rules
# generated from proprietary-files.txt BOOT_JAR entries. payjoy-api is omitted
# because its corresponding stock service is outside this prototype.
