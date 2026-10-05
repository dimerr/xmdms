# XMDMS

Cross-platform desktop manager for Xiongmai (XM) NVR/DVR/IPC devices.

Single-file PySide6 application (`xmdms.py`) that talks to devices over the
NETIP protocol (`dvrip.py`) and the vendor HTTP/RTSP services:

- LAN discovery (broadcast) and cloud/SN devices (optional `xmcloud.py`)
- Network, System, Display, Encode, Camera, Storage, RS232/485/PTZ, Users,
  Digital channels and Settings configuration
- Live video with audio: QtMultimedia (FFmpeg backend bundled with PySide6),
  optional PyAV / external ffmpeg fallbacks, G.711A audio with mute + volume
- Digital-channel IPC provisioning over the NVR (`OPDIGSetIP`)
- UDP IP provisioning for discovered devices (`Provision`, 2 attempts,
  per-row success/failure feedback)
- Config export/import and factory reset

## Layout

| Path | Purpose |
| --- | --- |
| `xmdms.py` | application (single file) |
| `dvrip.py` | NETIP protocol client (vendored, required) |
| `xmcloud.py` | optional cloud/RPS transport patch (not distributed) |
| `tools/make_icon.py` | build-time icon generator (`xmdms.ico`) |
| `xmdms.spec` | PyInstaller spec (Windows, onedir) |
| `build_windows.bat` | local Windows build |
| `.github/workflows/windows-build.yml` | CI build on every push |

`dvrip.py` and `xmcloud.py` are loaded from the application directory only.

## Run from source

```
pip install -r requirements.txt
python xmdms.py
```

## Build for Windows

PyInstaller cannot cross-compile; run this on Windows (or let CI do it):

```
build_windows.bat
```

Output: `dist\xmdms\xmdms.exe` (onedir). The GitHub Actions workflow builds
the same artifact on every push and uploads `xmdms-windows-x64.zip`.

## Notes

- Cloud/RPS devices require `xmcloud.py` next to the application; it is not
  part of the distributed build.
- Live video uses the FFmpeg backend bundled with PySide6. The external
  `ffmpeg` fallback is only used if the Qt backend fails and no PyAV is
  installed.
- Config exports are written to `cfgs\` next to the executable when writable,
  otherwise to `%LOCALAPPDATA%\xmdm3\cfgs`.

## License

Proprietary, all rights reserved. See `LICENSE`.
