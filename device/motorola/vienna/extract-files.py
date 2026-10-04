#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
# SPDX-License-Identifier: Apache-2.0

"""Extract the reviewed vienna proprietary file list from a stock dump."""

from extract_utils.fixups_blob import blob_fixup
from extract_utils.main import ExtractUtils, ExtractUtilsModule


module = ExtractUtilsModule(
    "vienna",
    "motorola",
    blob_fixups={
        "system_ext/lib64/libimsma.so": blob_fixup().replace_needed(
            "libsink.so", "libsink-mtk.so"
        ),
    },
)


if __name__ == "__main__":
    ExtractUtils.device(module).run()
