#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SOURCE="${1:-$ROOT/.packaging/xmdms-1024.png}"
OUTPUT="${2:-$ROOT/.packaging/xmdms.icns}"
ICONSET="$ROOT/build/XMDMS.iconset"

if [ ! -f "$SOURCE" ]; then
    echo "missing icon source: $SOURCE" >&2
    exit 1
fi

rm -rf "$ICONSET"
mkdir -p "$ICONSET" "$(dirname "$OUTPUT")"
for size in 16 32 128 256 512; do
    sips -z "$size" "$size" "$SOURCE" \
        --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
    sips -z "$((size * 2))" "$((size * 2))" "$SOURCE" \
        --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o "$OUTPUT"
echo "wrote $OUTPUT"
