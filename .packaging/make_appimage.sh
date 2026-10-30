#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DIST="${1:-$ROOT/dist/xmdms}"
OUTPUT="${2:-$ROOT/dist/xmdms-linux-x86_64.AppImage}"
APPIMAGETOOL="${APPIMAGETOOL:-$ROOT/build/appimagetool}"

if [ ! -x "$APPIMAGETOOL" ]; then
    echo "appimagetool not found or not executable: $APPIMAGETOOL" >&2
    exit 1
fi
if [ ! -x "$DIST/xmdms" ]; then
    echo "PyInstaller output not found: $DIST/xmdms" >&2
    exit 1
fi
if [ ! -f "$ROOT/.packaging/xmdms.png" ]; then
    echo "missing icon: $ROOT/.packaging/xmdms.png" >&2
    exit 1
fi

mkdir -p "$ROOT/build" "$(dirname "$OUTPUT")"
WORK=$(mktemp -d "$ROOT/build/appimage.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
APPDIR="$WORK/AppDir"

mkdir -p \
    "$APPDIR/usr/bin" \
    "$APPDIR/usr/share/applications" \
    "$APPDIR/usr/share/icons/hicolor/256x256/apps"
cp -a "$DIST" "$APPDIR/usr/bin/xmdms"
cp "$ROOT/.packaging/xmdms.png" "$APPDIR/xmdms.png"
cp "$ROOT/.packaging/xmdms.png" \
    "$APPDIR/usr/share/icons/hicolor/256x256/apps/xmdms.png"
cp "$ROOT/.packaging/xmdms.desktop" "$APPDIR/xmdms.desktop"
cp "$ROOT/.packaging/xmdms.desktop" \
    "$APPDIR/usr/share/applications/xmdms.desktop"
cp "$ROOT/.packaging/AppRun" "$APPDIR/AppRun"
chmod +x "$APPDIR/AppRun"
ln -s xmdms.png "$APPDIR/.DirIcon"

ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 \
    "$APPIMAGETOOL" "$APPDIR" "$OUTPUT"
chmod +x "$OUTPUT"
echo "wrote $OUTPUT"
