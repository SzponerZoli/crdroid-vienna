#!/usr/bin/env bash
set -o pipefail

workspace_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$workspace_dir/crdroid"
status_file="$source_dir/out/build-systemimage.exit-code"
log_file="$source_dir/out/build-systemimage.log"

export PATH="$workspace_dir/tools/bin:$PATH"
export GOCACHE="$source_dir/.gocache"
export CCACHE_DIR="$source_dir/.ccache"
export CCACHE_MAXSIZE=20G

cd "$source_dir" || exit 1
mkdir -p out "$GOCACHE" "$CCACHE_DIR"
rm -f "$status_file"

if (($# == 0)); then
    set -- systemimage systemextimage productimage
fi

(
    source build/envsetup.sh
    lunch lineage_vienna bp4a userdebug
    mka "$@" -j8
) >"$log_file" 2>&1
result=$?
printf '%s\n' "$result" >"$status_file"
exit "$result"
