# SPDX-License-Identifier: Apache-2.0

# Prototype target for XT2409-1 RETEU W1UIS36H.39-25-8 only.
# The stock image prebuilts are staged by tools/stage_stock_images.py.
DEVICE_PATH := device/motorola/vienna
STOCK_IMAGES := $(DEVICE_PATH)/prebuilts

# Architecture and platform
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-2a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_VARIANT := generic
TARGET_BOARD_PLATFORM := mt6878
TARGET_BOOTLOADER_BOARD_NAME := vienna
TARGET_NO_BOOTLOADER := true
TARGET_SCREEN_DENSITY := 450

# Stock boot images and modules are retained until a matching kernel/module
# build and device ramdisk have been validated on the actual phone.
BOARD_BOOT_HEADER_VERSION := 4
BOARD_INIT_BOOT_HEADER_VERSION := 4
BOARD_KERNEL_PAGESIZE := 4096
BOARD_BOOTIMAGE_PARTITION_SIZE := 67108864
BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 67108864
BOARD_INIT_BOOT_IMAGE_PARTITION_SIZE := 8388608
BOARD_DTBOIMG_PARTITION_SIZE := 8388608
BOARD_PREBUILT_BOOTIMAGE := $(STOCK_IMAGES)/boot.img
BOARD_KERNEL_IMAGE_NAME := Image.gz
TARGET_PREBUILT_KERNEL := $(STOCK_IMAGES)/Image.gz
BOARD_PREBUILT_VENDOR_BOOTIMAGE := $(STOCK_IMAGES)/vendor_boot.img
BOARD_PREBUILT_INIT_BOOT_IMAGE := $(STOCK_IMAGES)/init_boot.img
BOARD_PREBUILT_DTBOIMAGE := $(STOCK_IMAGES)/dtbo.img
TARGET_NO_RECOVERY := true

# Build recovery resources in a separate product. The resulting fragment will
# be reviewed against the exact-model stock vendor_boot before any device test.
ifeq ($(TARGET_PRODUCT),lineage_vienna_recovery)
BOARD_MKBOOTIMG_ARGS := --header_version 4
BOARD_USES_GENERIC_KERNEL_IMAGE := true
BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true
BOARD_INCLUDE_RECOVERY_RAMDISK_IN_VENDOR_BOOT := true
BOARD_EXCLUDE_KERNEL_FROM_RECOVERY_IMAGE := true
BOARD_RAMDISK_USE_LZ4 := true
TARGET_RECOVERY_FSTAB := $(DEVICE_PATH)/recovery.fstab
BOARD_VENDOR_CMDLINE := bootopt=64S3,32N2,64N2
BOARD_INCLUDE_DTB_IN_BOOTIMG := true
BOARD_PREBUILT_DTBIMAGE_DIR := $(STOCK_IMAGES)/dtb
endif

# A/B and virtual A/B partition layout, measured from the phone's GPT and super.
# Keep the stock `main_a`/`main_b` group names for fastbootd and OTA updates.
AB_OTA_UPDATER := true
AB_OTA_PARTITIONS := \
    boot \
    dtbo \
    init_boot \
    product \
    system \
    system_dlkm \
    system_ext \
    vbmeta \
    vbmeta_system \
    vendor \
    vendor_boot \
    vendor_dlkm

BOARD_SUPER_PARTITION_SIZE := 23085449216
BOARD_SUPER_PARTITION_GROUPS := main
BOARD_MAIN_PARTITION_LIST := \
    product system system_dlkm system_ext vendor vendor_dlkm
BOARD_MAIN_SIZE := 23083352064

BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_SYSTEM_EXTIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_PRODUCTIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_VENDOR_DLKMIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_SYSTEM_DLKMIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := f2fs
TARGET_USERIMAGES_USE_F2FS := true
BOARD_USES_METADATA_PARTITION := true

TARGET_COPY_OUT_PRODUCT := product
TARGET_COPY_OUT_SYSTEM_EXT := system_ext
TARGET_COPY_OUT_VENDOR := vendor
TARGET_COPY_OUT_VENDOR_DLKM := vendor_dlkm
TARGET_COPY_OUT_SYSTEM_DLKM := system_dlkm

BOARD_PREBUILT_VENDORIMAGE := $(STOCK_IMAGES)/vendor.img
BOARD_PREBUILT_VENDOR_DLKMIMAGE := $(STOCK_IMAGES)/vendor_dlkm.img
BOARD_PREBUILT_SYSTEM_DLKMIMAGE := $(STOCK_IMAGES)/system_dlkm.img
BOARD_PREBUILT_VENDOR_BUILD_PROP := $(STOCK_IMAGES)/vendor.build.prop
BOARD_PREBUILT_VENDOR_DLKM_BUILD_PROP := $(STOCK_IMAGES)/vendor_dlkm.build.prop
BOARD_PREBUILT_SYSTEM_DLKM_BUILD_PROP := $(STOCK_IMAGES)/system_dlkm.build.prop
BOARD_PREBUILT_VENDOR_VINTF_DIR := $(STOCK_IMAGES)/vendor_vintf
BOARD_PREBUILT_ODM_VINTF_DIR := $(STOCK_IMAGES)/odm_vintf
BOARD_PREBUILT_ODM_VINTF_SKUS := dns

# Source policy base for the stock MediaTek services. The Motorola additions
# identified in research/sepolicy-crossrefs.json still need to be ported.
include device/mediatek/sepolicy_vndr/SEPolicy.mk
SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/private

# These images have not been boot-tested. AVB descriptors and policy integration
# still need a reviewed build and an unlocked test device.
BOARD_AVB_ENABLE := true
BOARD_AVB_KEY_PATH := external/avb/test/data/testkey_rsa2048.pem
BOARD_AVB_ALGORITHM := SHA256_RSA2048
# Keep the exact-firmware Motorola rollback level and bootloader metadata.
# The stock boot, init_boot, DTBO and vendor_boot payloads are reused here.
BOARD_AVB_ROLLBACK_INDEX := 25
BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --prop KERN_PROT_META:rodata_bounds:65536,16973824,29097984
BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --prop HAB_META:vienna_50
BOARD_AVB_MAKE_VBMETA_SYSTEM_IMAGE_ARGS += --prop KERN_PROT_META:rodata_bounds:65536,16973824,29097984
BOARD_AVB_MAKE_VBMETA_SYSTEM_IMAGE_ARGS += --prop HAB_META:vienna_50
BOARD_AVB_VBMETA_SYSTEM := system system_ext
BOARD_AVB_VBMETA_SYSTEM_KEY_PATH := external/avb/test/data/testkey_rsa2048.pem
BOARD_AVB_VBMETA_SYSTEM_ALGORITHM := SHA256_RSA2048
BOARD_AVB_VBMETA_SYSTEM_ROLLBACK_INDEX := 25
BOARD_AVB_VBMETA_SYSTEM_ROLLBACK_INDEX_LOCATION := 2
