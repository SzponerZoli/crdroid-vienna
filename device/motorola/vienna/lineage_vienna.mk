# SPDX-License-Identifier: Apache-2.0

$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

$(call inherit-product, device/motorola/vienna/device.mk)
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

# Keep the exact-model stock vendor_boot until its ramdisk and DTB can be
# rebuilt and validated. Header v4 otherwise makes Android build a new one.
PRODUCT_BUILD_VENDOR_BOOT_IMAGE := false

# Keep the inherited vendorcompat exclusion to avoid duplicate protobuf
# modules, and explicitly include the host prebuilts under misc/common.
PRODUCT_SOURCE_ROOT_DIRS := -kernel/platform prebuilts/misc/common -prebuilts/misc/protobuf_vendorcompat

PRODUCT_NAME := lineage_vienna
PRODUCT_DEVICE := vienna
PRODUCT_BRAND := motorola
PRODUCT_MANUFACTURER := motorola
PRODUCT_MODEL := motorola edge 50 neo
