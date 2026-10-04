# SPDX-License-Identifier: Apache-2.0

# Host-only recovery experiment. Keep the normal ROM target unchanged.
$(call inherit-product, device/motorola/vienna/lineage_vienna.mk)

PRODUCT_NAME := lineage_vienna_recovery
PRODUCT_BUILD_VENDOR_BOOT_IMAGE := true
PRODUCT_BUILD_RECOVERY_IMAGE := true
