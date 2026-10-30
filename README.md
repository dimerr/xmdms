# XMDMS

Cross-platform desktop manager for Xiongmai (XM) NVR, DVR and IP camera
devices. XMDMS talks to devices over the NETIP/DVRIP protocol and covers
discovery, bulk provisioning, configuration, live view and maintenance in a
single PySide6 UI.

## Highlights

- Discover devices by UDP broadcast on a selected network interface.
- Inventory, sort, export and manually manage discovered devices.
- Provision IP addresses and change passwords in bulk.
- Edit network, system, video, camera, storage, user and serial/PTZ settings.
- Watch live video, listen to audio, record streams and save snapshots.
- Back up/restore configuration, inspect logs and run firmware utilities.
- English and Russian UI, light/dark themes and persistent preferences.

## Discovery and inventory

- UDP broadcast discovery with a configurable timeout (1–600 s) and number of
  search attempts (probes). The search runs until stopped or the configured
  window expires.
- Device table with IP, MAC, serial number, firmware version, build date and
  host name. Columns are sortable and rows are selectable with checkboxes.
- Search again removes devices that no longer answer, while manual entries are
  kept.
- Double-click a row to connect. Right-click for copy, select all/deselect all,
  add, modify, delete and clear.
- Add devices manually by IP address and port, with per-device login and
  password.
- Export the current inventory to CSV.

## Bulk operations

- **Provision** assigns consecutive IP addresses starting from the configured
  Start IP (automatically suggested as the selected device IP + 1). Each device
  gets two attempts with per-row progress and success/failure feedback.
- **Change** sets a new password on all checked devices, or on the selected
  device when nothing is checked.
- **Digital channels** manages downstream IP cameras on an NVR/DVR: search
  local NETIP/ONVIF cameras through the recorder, add all IPC, edit channel
  mappings and credentials, and provision IP addresses.

## Configuration tabs

| Tab | What it covers |
| --- | --- |
| **Network** | LAN address, subnet, gateway, DHCP/DNS, HTTP/TCP/RTSP/ONVIF ports, Wi-Fi scan and security, UPnP, SmartNet, PMS, VNIC, NAT/RPS, NTP, firmware upload and cloud upgrade. |
| **System** | Hardware/software/cloud ID, runtime age, channel count, device type, NAT status, TV standard, device language, restart schedule, time zone, date/time format, beeper, face/debug flags, audio input, cloud-ID QR code, time sync, reboot, config import/export/reset, device logs and firmware utilities. |
| **Display** | Video output resolution, GUI feature flags and window alpha. |
| **Encode** | Per-channel main stream and substream: H.264/H.265, resolution, FPS, CBR/VBR rate control, quality, bitrate, I-frame interval, smart H.265+/H.265AI, audio/video enable. Includes an all-channels editor. |
| **Camera** | Day/night mode, white balance, BLC, aperture, exposure, shutter, gain, AE sensitivity, day/night noise filters, IR-cut, DNC threshold, DWDR, flip/mirror, flicker rejection and white-light controls. |
| **Storage** | Disk list, read/write, read-only, redundant and snapshot modes, format and recover actions. |
| **Users** | User and group lists, add/modify/delete users and groups, and change user passwords. |
| **RS232/485/PTZ** | RS232 function and serial parameters, per-channel PTZ protocol/address/serial settings, and RS485 configuration. |
| **Settings** | Theme, language, password masking, search timeout and search attempts. |

Configuration is loaded from the device when a tab is opened and applied with
**Save**. Unsupported options depend on device firmware and may be rejected or
ignored by the device.

## Live view and media

- NETIP live video with selectable channel and Main/Sub stream.
- Video decoding through QtMultimedia/FFmpeg by default, with optional PyAV or
  a system `ffmpeg` fallback. Set `XMDM_VIDEO_BACKEND=qt|av|ffmpeg` to force a
  backend.
- G.711A audio playback with mute and volume controls.
- Raw stream recording to H.264, H.265, MJPEG or M4V files while watching.
- Snapshot popup with right-click **Save image...** (JPEG/PNG).
- RTSP URL copy/open for the selected channel and stream.

## Maintenance and diagnostics

- View and erase device logs.
- Export/import device configuration files and reset selected configuration
  sections or perform a factory reset.
- Upload firmware from a local file, or start the device's cloud upgrade.
- Build an XM recovery image (`.img`) or a flat flash dump (`.dump`) from an
  XM firmware `.bin` package for offline recovery work.
- Inspect raw NETIP request/response traffic in the **Query console**.
- Synchronize device time, reboot devices and change passwords.

## Settings

- Theme: **Auto** (follows the system color scheme), **Light** or **Dark**.
- Language: **Auto**, **English** or **Русский**. Auto follows the system
  locale.
- Password fields can be shown or masked.
- Search timeout (1–600 s) and search attempts (minimum 3) are editable and
  persisted.
- Preferences and last-used folders are saved with `QSettings` and restored on
  the next launch.

## Requirements

- Python 3.10 or newer for running from source (the Windows CI build uses
  Python 3.12).
- `PySide6==6.9.*`, `psutil`, `cryptography` and `qrcode` from
  `requirements.txt`.
- The required NETIP client `dvrip.py` must be supplied next to `xmdms.py`;
  it is not installed from PyPI.
- Optional: `av` for the PyAV video fallback, or a system `ffmpeg` executable
  for the external decoder.
- Network access to the device: TCP 34567 by default, UDP 34569 for discovery,
  and the configured HTTP/RTSP/ONVIF ports.

## Run from source

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
python3 xmdms.py
```

Place `dvrip.py` in the same directory as `xmdms.py` before starting the
application. Windows users can use `py -3.12` instead of `python3`.

## Build for Windows

PyInstaller cannot cross-compile; build on Windows (or let CI do it):

```bat
build_windows.bat
```

The script creates a virtual environment, installs dependencies, generates the
icon and produces a onedir build:

```
dist\xmdms\xmdms.exe
```

Requirements: Windows and Python 3.12 with the `py` launcher. The GitHub
Actions workflow
(`.github/workflows/windows-build.yml`) runs the same steps on every push or
manual dispatch and uploads `xmdms-windows-x64.zip`.

## Notes and limitations

- The device table and credentials are session-only; the app does not persist
  either. Use **Export** to keep an inventory. Manual entries are lost when the
  application closes.
- Available settings and actions depend on the device model and firmware.
- Linux/macOS packaging is not provided; run the source with a graphical Qt
  environment.
- If discovery finds nothing, select the correct interface, allow UDP 34569
  through the firewall, and confirm the device is on the same subnet.
- If video fails to start, install a Qt multimedia backend or a system
  `ffmpeg`, or try `XMDM_VIDEO_BACKEND=av`/`ffmpeg`.

## Safety

Use XMDMS only on devices you own or are explicitly authorized to manage.
Changing network settings, provisioning addresses, upgrading firmware,
resetting configuration and formatting storage can disconnect or erase data.
Double-check the selected devices and keep configuration backups before
performing destructive actions.
