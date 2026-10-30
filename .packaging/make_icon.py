#!/usr/bin/env python3
"""Generate icon files for builds from the SVG embedded in xmdms.py."""
import base64
import os
import struct
import sys

if sys.platform != "win32":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QBuffer, QRectF, QSize, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import xmdms  # noqa: E402

SIZES = (16, 24, 32, 48, 64, 128, 256)


def render_png(renderer, size):
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    source = renderer.defaultSize()
    if source.isEmpty():
        source = QSize(603, 162)
    height = max(1, round(size * source.height() / source.width()) + 5)
    target = QRectF(0.0, (size - height) / 2.0, float(size), float(height))
    painter = QPainter(image)
    renderer.render(painter, target)
    painter.end()
    buffer = QBuffer()
    buffer.open(QBuffer.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def main():
    QApplication.instance() or QApplication([])
    renderer = QSvgRenderer(base64.b64decode(xmdms.APP_ICON_SVG_B64))
    if not renderer.isValid():
        print("error: embedded SVG is invalid", file=sys.stderr)
        return 1
    entries = [(size, render_png(renderer, size)) for size in SIZES]
    header = struct.pack("<HHH", 0, 1, len(entries))
    offset = 6 + 16 * len(entries)
    directory = bytearray()
    data = bytearray()
    for size, png in entries:
        value = 0 if size >= 256 else size
        directory += struct.pack(
            "<BBBBHHII", value, value, 0, 0, 1, 32, len(png), offset)
        offset += len(png)
        data += png
    out = os.path.join(HERE, "xmdms.ico")
    with open(out, "wb") as handle:
        handle.write(header + bytes(directory) + bytes(data))
    print("wrote %s (%d bytes)" % (
        out, len(header) + len(directory) + len(data)))
    if "--png" in sys.argv[1:]:
        for size, name in ((256, "xmdms.png"), (1024, "xmdms-1024.png")):
            path = os.path.join(HERE, name)
            with open(path, "wb") as handle:
                handle.write(render_png(renderer, size))
            print("wrote %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
