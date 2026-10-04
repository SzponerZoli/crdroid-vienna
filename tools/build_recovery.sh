#!/usr/bin/env bash
set -o pipefail

workspace_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$workspace_dir/crdroid"
export OUT_DIR=out-recovery
export PATH="$workspace_dir/tools/bin:$PATH"
export GOCACHE="$source_dir/.gocache"
export CCACHE_DIR="$source_dir/.ccache"
export CCACHE_MAXSIZE=20G

mkdir -p "$source_dir/$OUT_DIR" "$GOCACHE" "$CCACHE_DIR"
cd "$source_dir" || exit 1

(
    source build/envsetup.sh
    lunch lineage_vienna_recovery bp4a userdebug
    mka vendorbootimage -j8
) >"$source_dir/$OUT_DIR/build-recovery.log" 2>&1
result=$?
printf '%s\n' "$result" >"$source_dir/$OUT_DIR/build-recovery.exit-code"
exit "$result"
