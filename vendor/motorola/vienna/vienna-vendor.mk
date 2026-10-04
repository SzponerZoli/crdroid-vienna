#
# Automatically generated file. DO NOT MODIFY
#

PRODUCT_SOONG_NAMESPACES += \
    vendor/motorola/vienna

PRODUCT_COPY_FILES += \
    vendor/motorola/vienna/proprietary/system/etc/permissions/moto-telephony.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/moto-telephony.xml \
    vendor/motorola/vienna/proprietary/system_ext/etc/init/android.hardware.audio.parameter_parser.service.rc:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/init/android.hardware.audio.parameter_parser.service.rc \
    vendor/motorola/vienna/proprietary/system_ext/etc/init/init.thermald.rc:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/init/init.thermald.rc \
    vendor/motorola/vienna/proprietary/system_ext/etc/init/init.vtservice.rc:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/init/init.vtservice.rc \
    vendor/motorola/vienna/proprietary/system_ext/etc/init/terserver.rc:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/init/terserver.rc \
    vendor/motorola/vienna/proprietary/system_ext/etc/permissions/com.mediatek.ims.rcsua.xml:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/permissions/com.mediatek.ims.rcsua.xml \
    vendor/motorola/vienna/proprietary/system_ext/etc/permissions/privapp-permissions-com.motorola.rcsConfigService.xml:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/permissions/privapp-permissions-com.motorola.rcsConfigService.xml \
    vendor/motorola/vienna/proprietary/system_ext/etc/permissions/system-ext-permissions-mediatek.xml:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/permissions/system-ext-permissions-mediatek.xml \
    vendor/motorola/vienna/proprietary/system_ext/etc/sysconfig/com.mediatek.ims.config.xml:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/sysconfig/com.mediatek.ims.config.xml \
    vendor/motorola/vienna/proprietary/system_ext/etc/sysconfig/whitelist_com.motorola.rcsConfigService.xml:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/sysconfig/whitelist_com.motorola.rcsConfigService.xml

PRODUCT_PACKAGES += \
    libcomutils \
    libimsma \
    libimsma_adapt \
    libimsma_rtp \
    libimsma_socketwrapper \
    libmtk_vt_service \
    libmtk_vt_wrapper \
    libsignal \
    libsink-mtk \
    libsource \
    libterservice \
    libvcodec_cap \
    libvcodec_capenc \
    libvt_avsync \
    vendor.mediatek.hardware.videotelephony-V1-ndk \
    vendor.mediatek.hardware.videotelephony@1.0 \
    OP12Ims \
    mediatek-res \
    ImsService \
    MtkCapCtrl \
    MtkGbaService \
    MtkTelephonyAssist \
    RcsUaService \
    rcsConfigService \
    moto-telephony \
    CapCtrlInterface \
    com.mediatek.ims.rcsua \
    mediatek-carrier-config-manager \
    mediatek-common \
    mediatek-framework \
    mediatek-ims-base \
    mediatek-ims-oem-plugin \
    mtk-moto-ims-ext \
    mtk-moto-telephony-ext \
    mtk-telephony-common \
    android.hardware.audio.parameter_parser.service \
    terservice \
    thermald \
    vtservice

PRODUCT_BOOT_JARS += \
    system_ext:mediatek-carrier-config-manager \
    system_ext:mediatek-common \
    system_ext:mediatek-framework \
    system_ext:mediatek-ims-base
