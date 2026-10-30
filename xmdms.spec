# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for xmdms (Windows, onedir)."""
import os

import PySide6

qt_root = os.path.join(os.path.dirname(PySide6.__file__), "Qt")

# QtMultimedia FFmpeg backend: plugin + shared libraries.  The PySide6
# hooks usually collect these; keep an explicit copy as a safety net.
extra_binaries = []
plugin = os.path.join(qt_root, "plugins", "multimedia", "ffmpegmediaplugin.dll")
if os.path.isfile(plugin):
    extra_binaries.append(
        (plugin, os.path.join("PySide6", "Qt", "plugins", "multimedia")))
bin_dir = os.path.join(qt_root, "bin")
if os.path.isdir(bin_dir):
    for name in sorted(os.listdir(bin_dir)):
        lower = name.lower()
        if lower.endswith(".dll") and lower.startswith(("av", "sw")):
            extra_binaries.append(
                (os.path.join(bin_dir, name), os.path.join("PySide6", "Qt", "bin")))

a = Analysis(
    ["xmdms.py"],
    pathex=[],
    binaries=extra_binaries,
    datas=[],
    hiddenimports=["dvrip", "qrcode", "PySide6.QtSvg"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "av",
        "numpy",
        "xmcloud",
        "colorama",
        "tkinter",
        "PIL",
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebEngineQuick",
        "PySide6.QtQml",
        "PySide6.QtQuick",
        "PySide6.QtQuickWidgets",
        "PySide6.Qt3DCore",
        "PySide6.Qt3DRender",
        "PySide6.QtCharts",
        "PySide6.QtDataVisualization",
        "PySide6.QtPdf",
        "PySide6.QtPdfWidgets",
        "PySide6.QtWebSockets",
        "PySide6.QtWebChannel",
        "PySide6.QtSql",
        "PySide6.QtTest",
        "PySide6.QtBluetooth",
        "PySide6.QtPositioning",
        "PySide6.QtSerialPort",
        "PySide6.QtSensors",
        "PySide6.QtDesigner",
        "PySide6.QtHelp",
        "PySide6.QtUiTools",
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="xmdms",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="xmdms.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="xmdms",
)
