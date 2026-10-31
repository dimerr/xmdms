import base64
import calendar
import csv
import hashlib
import importlib.util
import io
import ipaddress
import json
import math
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request
import zipfile
from collections import deque
from datetime import datetime, timedelta
from urllib.parse import quote

from PySide6.QtCore import (
    QAbstractTableModel,
    QEvent,
    QIODevice,
    QModelIndex,
    QObject,
    QRect,
    QRectF,
    QSettings,
    QSize,
    Qt,
    QThread,
    QTimer,
    QUrl,
    Signal,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QDesktopServices,
    QIcon,
    QImage,
    QIntValidator,
    QPainter,
    QPalette,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QStyle,
    QStyleOptionButton,
    QTableView,
    QTableWidget,
    QTextBrowser,
    QTableWidgetItem,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from i18n import (
    load_language,
    resolve_language,
    set_language,
    tr,
)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

GITHUB_REPO = "dimerr/xmdms"
GITHUB_PROFILE = "https://github.com/dimerr"
BASE_VERSION = "1.0"


def _detect_build_info():
    # A source checkout always reflects its own HEAD; build_info.py is for
    # frozen builds (or source archives) where .git is not available.
    if os.path.isdir(os.path.join(HERE, ".git")):
        try:
            count = subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=HERE, text=True, timeout=3).strip()
            commit = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=HERE, text=True, timeout=3).strip()
            date = subprocess.check_output(
                ["git", "show", "-s", "--format=%cs", "HEAD"],
                cwd=HERE, text=True, timeout=3).strip()
            timestamp = subprocess.check_output(
                ["git", "show", "-s", "--format=%cI", "HEAD"],
                cwd=HERE, text=True, timeout=3).strip()
            if count.isdigit():
                return ("%s.%d" % (BASE_VERSION, int(count)), commit, date,
                        timestamp)
        except Exception:
            pass
    try:
        import build_info
        version = str(getattr(build_info, "VERSION", "") or "").strip()
        if version:
            return (
                version,
                str(getattr(build_info, "COMMIT", "") or "").strip(),
                str(getattr(build_info, "BUILD_DATE", "") or "").strip(),
                str(getattr(build_info, "COMMIT_DATE", "") or "").strip(),
            )
    except ImportError:
        pass
    return "%s.0" % BASE_VERSION, "", "", ""


APP_VERSION, BUILD_COMMIT, BUILD_DATE, BUILD_TIMESTAMP = _detect_build_info()

try:
    import psutil
except ImportError:
    psutil = None

try:
    from dvrip import DVRIPCam
except ImportError:
    DVRIPCam = None

try:
    import qrcode
except ImportError:
    qrcode = None

try:
    from PySide6.QtMultimedia import (
        QAudioFormat,
        QAudioSink,
        QMediaDevices,
        QMediaPlayer,
    )
    from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
    QT_MULTIMEDIA = True
except Exception:
    QAudioFormat = None
    QAudioSink = None
    QMediaDevices = None
    QMediaPlayer = None
    QGraphicsVideoItem = None
    QT_MULTIMEDIA = False

try:
    import av
    AV_AVAILABLE = True
except Exception:
    av = None
    AV_AVAILABLE = False

FFMPEG_BINARY = shutil.which("ffmpeg")

DISCOVERY_PORT = 34569
IPSEARCH_REQ = 1530
IPSEARCH_RSP = 1531
IP_SET_REQ = 1532
IP_SET_RSP = 1533
PROBE_INTERVAL = 1.0
SET_TIMEOUT = 3.0
CONNECTED_BRUSH = QBrush(QColor("#A5D6A7"))
PROVISION_OK_BRUSH = QBrush(QColor("#A5D6A7"))
PROVISION_FAILED_BRUSH = QBrush(QColor("#EF9A9A"))
PROVISION_ACTIVE_BRUSH = QBrush(QColor("#FFF59D"))
GROUP_BOX_STYLE = (
    "QGroupBox {"
    " border: 1px solid palette(mid);"
    " border-radius: 6px;"
    " margin-top: 7px;"
    " padding-top: 4px;"
    "}"
    "QGroupBox::title {"
    " subcontrol-origin: margin;"
    " subcontrol-position: top left;"
    " left: 10px;"
    " padding: 0 3px;"
    "}"
)
SET_COPY_FIELDS = (
    "HostName",
    "HttpPort",
    "MAC",
    "MaxBps",
    "MonMode",
    "SSLPort",
    "TCPMaxConn",
    "TCPPort",
    "TransferPlan",
    "UDPPort",
    "UseHSDownLoad",
)
SYSTEM_GENERAL_KEYS = {
    "tv_standard": ("VideoStandard", "VideoFormat", "TVStandard"),
    "language": ("Language",),
    "timezone": ("TimeZone", "TimeZoneOffset"),
    "date_format": ("DateFormat",),
    "separator": ("Separator", "DateSeparator"),
    "time_format": ("TimeFormat", "HourFormat"),
}
TIME_ZONE_CHOICES = (
    ("UTC-12:00", -720),
    ("UTC-11:00", -660),
    ("UTC-10:00", -600),
    ("UTC-09:00", -540),
    ("UTC-08:00", -480),
    ("UTC-07:00", -420),
    ("UTC-06:00", -360),
    ("UTC-05:00", -300),
    ("UTC-04:00", -240),
    ("UTC-03:30", -210),
    ("UTC-03:00", -180),
    ("UTC-02:00", -120),
    ("UTC-01:00", -60),
    ("UTC+00:00", 0),
    ("UTC+01:00", 60),
    ("UTC+02:00", 120),
    ("UTC+03:00", 180),
    ("UTC+03:30", 210),
    ("UTC+04:00", 240),
    ("UTC+04:30", 270),
    ("UTC+05:00", 300),
    ("UTC+05:30", 330),
    ("UTC+05:45", 345),
    ("UTC+06:00", 360),
    ("UTC+06:30", 390),
    ("UTC+07:00", 420),
    ("UTC+08:00", 480),
    ("UTC+09:00", 540),
    ("UTC+09:30", 570),
    ("UTC+10:00", 600),
    ("UTC+11:00", 660),
    ("UTC+12:00", 720),
    ("UTC+13:00", 780),
)
GUI_SET_KEYS = (
    "AlarmGlint", "AlarmStateEnable", "CarInfo", "ChanStateBitRateEnable",
    "ChanStateLckEnable", "ChanStateMtdEnable", "ChanStateRecEnable",
    "ChanStateVlsEnable", "ChanWindowGridEnable", "ChannelTitleEnable",
    "Deflick", "GPSInfo", "QRcodeEnable", "RecordStateEnable",
    "RemoteEnable", "TimeTitleEnable",
)
ENCODE_CODECS = ("H.264", "H.265")
ENCODE_RESOLUTIONS = ("4K", "6M", "5M", "4M", "3M", "1080P", "1080N", "960P",
                      "720P", "960H", "D1", "HD1", "CIF", "QCIF", "VGA", "QVGA",
                      "2.5M", "NHD", "WSVGA", "4K-N", "5M-N", "4M-N", "3M-N")
ENCODE_RATE_CONTROL = ("CBR", "VBR")
ENCODE_IFRAME_EQ_PFRAME = 10
ENCODE_RESOLUTION_ALIASES = {
    "960H": "650TVL", "650TVL": "650TVL",
    "960P": "1_3M", "1.3M": "1_3M", "1_3M": "1_3M",
    "2.5M": "2_5M", "2_5M": "2_5M",
    "3M-N": "3M_N", "3M_N": "3M_N",
    "4M-N": "4M_N", "4M_N": "4M_N",
    "5M-N": "5M_N", "5M_N": "5M_N",
    "4K-N": "4K_N", "4K_N": "4K_N",
}
SERIAL_BAUD_RATES = ("1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200")
SERIAL_DATA_BITS = ("5", "6", "7", "8")
SERIAL_STOP_BITS = ("1", "2")
SERIAL_PARITY = ("None", "Odd", "Even", "Mark", "Space")
TAB_FETCH_KEYS = (
    ("Network", ("common", "dhcp", "adaptive", "dns", "smartnet", "wifi", "rtsp",
                 "online_upgrade", "upnp", "onvif_pwd", "pms", "ntp", "pubcfg",
                 "caps", "force_dhcp", "disable_xm_server", "nat", "ability",
                 "oemcfg")),
    ("System", ("system", "common", "general", "system_timezone", "languages",
                "max_preview", "ability", "device_desc", "nat_info",
                "chn_status")),
    ("Display", ("video_out", "gui_set", "vga_resolution", "ability", "device_desc")),
    ("Encode", ("system", "general", "chn_status", "encode_channels",
                "encode_smart", "encode_ability", "av_encode")),
    ("Camera", ("camera_param", "camera_ex_param", "white_light")),
    ("Storage", ("storage_info",)),
    ("RS232/485/PTZ", ("uart_comm", "uart_ptz", "uart_rs485", "com_protocol",
                       "ptz_protocol", "uart_protocol")),
    ("Users", ("users", "groups", "authority_list")),
)
STORAGE_COLUMNS = ("Disk", "Type", "Status", "Capacity", "Free", "Start", "End")
STORAGE_DRIVE_TYPES = {0: "RW", 1: "RO", 2: "Event",
                       3: "Redundant", 4: "Snapshot"}
CAMERA_FIELD_PATHS = {
    "ExposureLevel": ("ExposureParam", "Level"),
    "AutoGain": ("GainParam", "AutoGain"),
    "Gain": ("GainParam", "Gain"),
}
CAMERA_EX_FIELD_PATHS = {
    "AutomaticAdjustment": (None, "AutomaticAdjustment"),
    "Style": (None, "Style"),
    "DWDR": ("BroadTrends", "AutoGain"),
    "DWDRGain": ("BroadTrends", "Gain"),
}
WHITE_LIGHT_FIELD_PATHS = {
    "MoveTrigLevel": ("MoveTrigLight", "Level"),
    "MoveTrigDuration": ("MoveTrigLight", "Duration"),
    "PeriodEnable": ("WorkPeriod", "Enable"),
    "StartHour": ("WorkPeriod", "SHour"),
    "StartMinute": ("WorkPeriod", "SMinute"),
    "EndHour": ("WorkPeriod", "EHour"),
    "EndMinute": ("WorkPeriod", "EMinute"),
}
ENCODE_RESOLUTION_BITS = (
    "D1", "HD1", "BCIF", "CIF", "QCIF", "VGA", "QVGA", "SVCD",
    "QQVGA", "ND1", "650TVL", "720P", "1_3M", "UXGA", "1080P", "WUXGA",
    "2_5M", "3M", "5M", "1080N", "4M", "6M", "8M", "12M",
    "4K", "720N", "WSVGA", "NHD", "3M_N", "4M_N", "5M_N", "4K_N",
)
ENCODE_BITRATE_TABLES = {
    "h264": {
        "D1": (512, 768, 1024, 1536, 2048, 2560),
        "HD1": (384, 512, 768, 1024, 1536, 2048),
        "BCIF": (384, 512, 768, 1024, 1536, 2048),
        "CIF": (64, 192, 384, 512, 768, 1024),
        "QCIF": (64, 128, 192, 384, 448, 512),
        "VGA": (512, 768, 896, 1280, 1536, 2048),
        "QVGA": (256, 384, 512, 640, 768, 1024),
        "SVCD": (512, 768, 896, 1280, 1536, 2048),
        "QQVGA": (64, 128, 192, 384, 448, 512),
        "ND1": (64, 128, 256, 448, 512, 768),
        "650TVL": (896, 1024, 1536, 2048, 3072, 4096),
        "720P": (1024, 1536, 2048, 2560, 3072, 4096),
        "1_3M": (1024, 1536, 2048, 3072, 4096, 5120),
        "UXGA": (1024, 2048, 3072, 4096, 6144, 8192),
        "1080P": (1024, 2048, 3072, 4096, 6144, 8192),
        "WUXGA": (1177, 2355, 3532, 4710, 7065, 10240),
        "2_5M": (1280, 2560, 3840, 5120, 7680, 10240),
        "3M": (1536, 3072, 4096, 6144, 8192, 10240),
        "5M": (2048, 3072, 4096, 6144, 8192, 10240),
        "1080N": (1024, 1536, 2048, 2560, 3072, 4096),
        "4M": (1536, 3072, 4096, 6144, 8192, 10240),
        "6M": (1536, 3072, 4096, 6144, 8192, 10240),
        "8M": (1536, 3072, 4096, 6144, 8192, 10240),
        "12M": (1536, 3072, 4096, 6144, 8192, 10240),
        "4K": (2048, 4096, 6144, 8192, 11264, 13312),
        "720N": (512, 768, 1024, 1536, 2048, 2560),
        "WSVGA": (1024, 1536, 2048, 2560, 3072, 4096),
        "NHD": (512, 768, 896, 1280, 1536, 2048),
        "3M_N": (1024, 1536, 2048, 3072, 4096, 5120),
        "4M_N": (1024, 2048, 3072, 4096, 6144, 8192),
        "5M_N": (1280, 2560, 3840, 5120, 7680, 10240),
        "4K_N": (1536, 3072, 4096, 6144, 8192, 10240),
    },
    "h265": {
        "D1": (332, 499, 665, 998, 1331, 1664),
        "HD1": (249, 332, 499, 665, 998, 1331),
        "BCIF": (249, 332, 499, 665, 998, 1331),
        "CIF": (41, 124, 249, 332, 499, 665),
        "QCIF": (41, 83, 124, 249, 291, 332),
        "VGA": (332, 499, 582, 832, 998, 1331),
        "QVGA": (166, 249, 332, 416, 499, 665),
        "SVCD": (332, 499, 582, 832, 998, 1331),
        "QQVGA": (41, 83, 124, 249, 291, 332),
        "ND1": (41, 83, 166, 291, 332, 499),
        "650TVL": (582, 665, 998, 1331, 1996, 2662),
        "720P": (665, 998, 1331, 1664, 1996, 2662),
        "1_3M": (665, 998, 1331, 1996, 2662, 3328),
        "UXGA": (665, 1331, 1996, 2662, 3993, 5324),
        "1080P": (665, 1331, 1996, 2662, 3993, 5324),
        "WUXGA": (765, 1530, 2295, 3061, 4592, 6656),
        "2_5M": (832, 1664, 2496, 3328, 4992, 6656),
        "3M": (998, 1996, 2662, 3993, 5324, 6656),
        "5M": (1331, 1996, 2662, 3993, 5324, 6656),
        "1080N": (665, 998, 1331, 1664, 1996, 2662),
        "4M": (998, 1996, 2662, 3993, 5324, 6656),
        "6M": (998, 1996, 2662, 3993, 5324, 6656),
        "8M": (998, 1996, 2662, 3993, 5324, 6656),
        "12M": (998, 1996, 2662, 3993, 5324, 6656),
        "4K": (1331, 2662, 3993, 5324, 7321, 8652),
        "720N": (332, 499, 665, 998, 1331, 1664),
        "WSVGA": (582, 665, 998, 1331, 1996, 2662),
        "NHD": (332, 499, 582, 832, 998, 1327),
        "3M_N": (665, 998, 1331, 1996, 2662, 3328),
        "4M_N": (665, 1331, 1996, 2662, 3993, 5324),
        "5M_N": (832, 1664, 2496, 3328, 4992, 6656),
        "4K_N": (1331, 1996, 2665, 3993, 5324, 6656),
    },
}


def encode_vbr_bitrate(resolution, compression, quality, fps, gop, max_fps):
    table = ENCODE_BITRATE_TABLES["h265" if "265" in str(compression) else "h264"]
    name = str(resolution or "").strip().upper()
    name = ENCODE_RESOLUTION_ALIASES.get(name, name)
    values = table.get(name)
    if not values:
        return None
    try:
        index = int(quality) - 1
        fps = int(fps)
        gop = int(gop)
        max_fps = int(max_fps)
    except (TypeError, ValueError):
        return None
    index = max(0, min(len(values) - 1, index))
    if fps < 1 or gop < 1 or max_fps < 1:
        return None
    base = values[index]
    return base * (gop * fps + ENCODE_IFRAME_EQ_PFRAME - 1) // (
        gop * max_fps + ENCODE_IFRAME_EQ_PFRAME - 1)
SOFIA_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
RESULT_CODES = {
    100: "OK",
    101: "Unknown error",
    102: "Version not supported",
    103: "Illegal request",
    105: "User is not logged in",
    106: "Username or password is incorrect",
    107: "Insufficient permission",
    108: "Timeout",
    117: "Message is malformed",
    150: "Success, device restart required",
    202: "User is not logged in",
    203: "Password is incorrect",
    204: "User is illegal",
    205: "User is locked",
    208: "Invalid input",
    502: "Illegal command",
    602: "Need to restart the application",
    603: "Need to restart the system",
    604: "Error writing file",
    605: "Feature not supported",
    606: "Verification failed",
    607: "Configuration does not exist",
    608: "Configuration parsing error",
}


APP_ICON_SVG_B64 = (
    "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+Cjwh"
    "LS0gQ3JlYXRlZCB3aXRoIElua3NjYXBlIChodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy8pIC0tPgoK"
    "PHN2ZwogICB2ZXJzaW9uPSIxLjEiCiAgIGlkPSJzdmcyIgogICB3aWR0aD0iNjAzLjg0ODQ1Igog"
    "ICBoZWlnaHQ9IjE2MiIKICAgdmlld0JveD0iMCAwIDYwMy44NDg0NSAxNjIiCiAgIHhtbG5zPSJo"
    "dHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9y"
    "Zy8yMDAwL3N2ZyI+CiAgPGRlZnMKICAgICBpZD0iZGVmczYiIC8+CiAgPGcKICAgICBpZD0iZzgi"
    "CiAgICAgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTU3LjkyNTMwMiwtNjMuODc3Mjg5KSI+CiAgICA8"
    "cGF0aAogICAgICAgc3R5bGU9ImZpbGw6I2M5MjkxYztmaWxsLW9wYWNpdHk6MSIKICAgICAgIGQ9"
    "Im0gNTguMTM3MTk1LDIyNS4zODA1NCBjIDAsLTAuNDQyNzEgMTQuOTIyOTQzLC0yNC43MzM3NCAy"
    "OS45MjY5MTgsLTQ4LjcxMzk2IDMuODkzODQ4LC02LjIyMzM3IDEyLjAwMDA1NywtMTkuMjc1NTEg"
    "MjIuMzI3MjE3LC0zNS45NDk5NyBsIDYuNjAyNTgsLTEwLjY2MDY4IC0yMi41NzMyODksLTI1LjMz"
    "OTMyIEMgODIuMDA1MzE2LDkwLjc3OTk3OSA2OC43MTQ4OCw3NS44ODk3ODkgNjQuODg2MzIsNzEu"
    "NjI3Mjg5IGwgLTYuOTYxMDE4LC03Ljc1IDQ3Ljg1NTk0OCwxLjdlLTQgNDcuODU1OTUsMS42ZS00"
    "IDMzLjU4ODI4LDM3Ljc0OTg0MSBjIDE4LjQ3MzU1LDIwLjc2MjQxIDQ0LjQ1MjE1LDUwLjAxMDA4"
    "IDU3LjczMDIyLDY0Ljk5NDgzIDIzLjQwMDIzLDI2LjQwNzk1IDI0LjE4NTIxLDI3LjE3NjAzIDI1"
    "LjU1MDI3LDI1IDEuOTM3MTQsLTMuMDg3OTggMTAuODYzOSwtMTguMDkyNzggMjYuNjE5OTksLTQ0"
    "Ljc0NSA0NC4wNjY3NCwtNzQuNTQxMTIxIDQwLjE4MjQ5LC02OS4wNzAwNTEgNTMuNTExMjQsLTc1"
    "LjM3MjA1MSAxMi40NDg5OSwtNS44ODYwMyAxOS4wMDA0MiwtNy4xMjkzMyAzNy41LC03LjExNjU3"
    "IDE4LjA5ODcxLDAuMDEyNSAyNC4xMjQ4MywxLjI0Mjc4IDM3Ljg0OTU3LDcuNzI3NDEgMTAuMDgw"
    "OTUsNC43NjMwMiAxMy40NzMxNyw4LjkxMjkxIDI5LjY0MDc0LDM2LjI2MTIxMSA4LjEyODYzLDEz"
    "Ljc1IDE2LjY4MTQyLDI4LjE1IDE5LjAwNjIsMzIgMi4zMjQ3OSwzLjg1IDEyLjY3MywyMS40IDIy"
    "Ljk5NjA0LDM5IDEwLjMyMzAzLDE3LjYgMjAuNTEwMjcsMzQuODM4NDkgMjIuNjM4MywzOC4zMDc3"
    "NSAyLjEyODAzLDMuNDY5MjcgMy44NjkxNSw2LjczMTc3IDMuODY5MTUsNy4yNSAwLDAuNTc2Mzcg"
    "LTE3Ljc2NTA4LDAuOTMwNyAtNDUuNzUsMC45MTI1MSBsIC00NS43NSwtMC4wMjk3IC0zLjU2OTcz"
    "LC02LjIyMDI2IGMgLTEuOTYzMzYsLTMuNDIxMTggLTEwLjIzNTQzLC0xNy40NzAzIC0xOC4zODIz"
    "OSwtMzEuMjIwMyAtMTYuNDkyNTEsLTI3LjgzNTE4IC0yMy4zNDE1OSwtMzkuNDI4MTkgLTM1LjQ0"
    "NzYxLC02MCAtNC41MzEyNywtNy43IC04LjYyMTk4LC0xNC4zOTE5NCAtOS4wOTA0NSwtMTQuODcw"
    "OTggLTAuODk0MTYsLTAuOTE0MzIgLTIuNzI2MDYsMS44Njk3MiAtMTYuMzY1MDksMjQuODcwOTgg"
    "LTQuNTY1ODYsNy43IC0xNC44NTI3NiwyNS4wMjUgLTIyLjg1OTc3LDM4LjUgLTguMDA3MDEsMTMu"
    "NDc1IC0xNy44MjcsMzAuMDEyNSAtMjEuODIyMTksMzYuNzUgbCAtNy4yNjQsMTIuMjUgaCAtNDcu"
    "ODAzNzIgLTQ3LjgwMzcyIGwgLTE2Ljc5NTY3LC0xOC44MDY4NCBjIC05LjIzNzYxLC0xMC4zNDM3"
    "NiAtMjEuOTI0NzEsLTI0LjYzMTI2IC0yOC4xOTM1NiwtMzEuNzUgLTYuMjY4ODQsLTcuMTE4NzQg"
    "LTExLjY2ODg0LC0xMy4wNTI2MyAtMTIsLTEzLjE4NjQzIC0wLjMzMTE1LC0wLjEzMzgxIC05LjQy"
    "MTI3LDE0LjA0MTE5IC0yMC4yMDAyNSwzMS41IGwgLTE5LjU5ODE0LDMxLjc0MzI3IC0yMy42NTE4"
    "NjEsMC4yNjgxIGMgLTEzLjAwODUyLDAuMTQ3NDUgLTIzLjY1MTg1NCwwLjAyODMgLTIzLjY1MTg1"
    "NCwtMC4yNjQ4NSB6IE0gNTM4LjE0NzQsMTcxLjYwNTY5IGMgLTE3Ljg2OTQsLTI5LjgyNTYyIC0z"
    "OC4wMDY5LC02My4zMjYxNyAtNDQuNzUsLTc0LjQ0NTY3MSAtNi43NDMxMSwtMTEuMTE5NSAtMTIu"
    "MjYwMiwtMjAuNjM5MDUgLTEyLjI2MDIsLTIxLjE1NDU0IDAsLTEuNTY0NjEgMTAuMTYxODQsLTYu"
    "Nzg1NzQgMTguMDU5MDYsLTkuMjc4NjkgNi42Mjc3NCwtMi4wOTIyMiA5LjM1MzQ2LC0yLjM0ODk1"
    "IDI0Ljk0MDk0LC0yLjM0OTIxIDE4Ljc0MDMxLC0zLjFlLTQgMjUuMzczNTgsMS4yMDQ4NCAzOC4y"
    "MzI4Miw2Ljk0NjI4IDEyLjEzNDkyLDUuNDE4MDMgMTMuNDQzODQsNi45NzA5NCAzMC44MTAwNSwz"
    "Ni41NTM0MzEgNS42NTAzLDkuNjI1IDEyLjE3MDg5LDIwLjY1IDE0LjQ5MDE5LDI0LjUgMi4zMTkz"
    "MSwzLjg1IDguODI5NDMsMTQuODc1IDE0LjQ2Njk0LDI0LjUgNS42Mzc1MSw5LjYyNSAxMi4xNTIz"
    "OSwyMC42NSAxNC40Nzc1MiwyNC41IDEwLjA4ODQ5LDE2LjcwNDc2IDI0LjUzMzAyLDQxLjM2Mzg5"
    "IDI1LjEwOTI0LDQyLjg2NTQ5IDAuNTc0OTIsMS40OTgyMyAtMy4xOTYyNiwxLjYzMjcxIC00NS4y"
    "Mjk3NywxLjYxMjkxIGwgLTQ1Ljg1Njk5LC0wLjAyMTYgeiBNIDIxNy4xMzcyLDExOS4yMTU3NSBj"
    "IDAsLTEuMzU2OTkgMzIuMzQ1MjIsLTU0LjUzMzcxMSAzMy40MjE5NCwtNTQuOTQ2ODgxIDAuNjE2"
    "NzQsLTAuMjM2NjcgMTEuMzQ3MDIsLTAuMzA5MDkgMjMuODQ1MDcsLTAuMTYwOTQgbCAyMi43MjM3"
    "MywwLjI2OTM2IC0xNy4xNDExNCwyNy43NSAtMTcuMTQxMTMsMjcuNzUwMDAxIGggLTIyLjg1NDI0"
    "IGMgLTEyLjU2OTgzLDAgLTIyLjg1NDIzLC0wLjI5NzY5IC0yMi44NTQyMywtMC42NjE1NCB6Igog"
    "ICAgICAgaWQ9InBhdGgxNzIiIC8+CiAgPC9nPgo8L3N2Zz4K"
)


def _dark_palette():
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(150, 150, 150))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,
                     QColor(120, 120, 120))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText,
                     QColor(120, 120, 120))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText,
                     QColor(120, 120, 120))
    return palette


def apply_theme(app, theme):
    theme = str(theme or "auto").strip().lower()
    if theme == "auto":
        scheme = app.styleHints().colorScheme()
        theme = "dark" if scheme == Qt.ColorScheme.Dark else "light"
    app.setStyle("Fusion")
    if theme == "dark":
        app.setPalette(_dark_palette())
    else:
        app.setPalette(app.style().standardPalette())


def app_icon():
    try:
        from PySide6.QtSvg import QSvgRenderer
    except ImportError:
        return QIcon()
    data = base64.b64decode(APP_ICON_SVG_B64)
    renderer = QSvgRenderer(data)
    if not renderer.isValid():
        return QIcon()
    source = renderer.defaultSize()
    if source.isEmpty():
        source = QSize(603, 162)
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        height = max(1, round(size * source.height() / source.width())+5)
        target = QRectF(0.0, (size - height) / 2.0, float(size), float(height))
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter, target)
        painter.end()
        icon.addPixmap(pixmap)
    return icon


def build_probe():
    header = bytearray(20)
    header[0] = 0xFF
    header[14:16] = IPSEARCH_REQ.to_bytes(2, "little")
    return bytes(header)


PROBE = build_probe()

CLOUD_PATCH_FILES = ("xmcloud.py",)
CLOUD_DISPATCH_METHODS = ("connect", "send", "reassemble_bin_payload", "upgrade", "keep_alive")
_cloud_patch = None


def _import_cloud_patch():
    path = os.path.join(HERE, CLOUD_PATCH_FILES[0])
    if not os.path.isfile(path):
        raise RuntimeError(
            "xmcloud.py was not found next to the application — cloud/RPS "
            "support is not available.")
    spec = importlib.util.spec_from_file_location("xm_cloud_patch", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("xm_cloud_patch", module)
    spec.loader.exec_module(module)
    return module


def cloud_patch_available():
    """True when xmcloud.py sits next to the application."""
    return os.path.isfile(os.path.join(HERE, CLOUD_PATCH_FILES[0]))


def _cloud_dispatch(original, patched):
    def method(self, *args, **kwargs):
        if getattr(self, "_cloud_device", False):
            return patched(self, *args, **kwargs)
        return original(self, *args, **kwargs)
    return method


def load_cloud_patch():
    """Import the xmcloud-style monkey patch for cloud (SN) devices.

    Cameras marked with ``_cloud_device`` use the patched transport
    (RPS tunnel when the RPS environment variable is set, P2P otherwise);
    direct cameras keep the original dvrip methods.  The patch file can be
    overridden with the ``XM_CLOUD_PATCH`` environment variable.
    """
    global _cloud_patch
    if isinstance(_cloud_patch, Exception):
        raise _cloud_patch
    if _cloud_patch is not None:
        return _cloud_patch
    if DVRIPCam is None:
        raise RuntimeError("python-dvr (dvrip.py) is not available")
    uninstall_query_logger()
    originals = {
        name: getattr(DVRIPCam, name)
        for name in CLOUD_DISPATCH_METHODS
        if hasattr(DVRIPCam, name)
    }
    try:
        module = _import_cloud_patch()
    except Exception as error:
        _cloud_patch = error
        install_query_logger()
        raise
    for name, original in originals.items():
        patched = getattr(DVRIPCam, name)
        if patched is not original:
            setattr(DVRIPCam, name, _cloud_dispatch(original, patched))
    install_query_logger()
    _cloud_patch = module
    return module


def load_private_extension(window):
    """Load the optional local ``priv.py`` next to the application.

    The file is deliberately not imported statically: PyInstaller never
    collects it, so it cannot leak into a public build.  It is also
    gitignored and local-only.  ``priv.py`` must define
    ``install(window, app)`` where ``app`` is this running module.
    """
    bases = []
    try:
        bases.append(window._app_dir())
    except Exception:
        pass
    if HERE not in bases:
        bases.append(HERE)
    path = ""
    for base in bases:
        candidate = os.path.join(base, "priv.py")
        if os.path.isfile(candidate):
            path = candidate
            break
    if not path:
        return
    try:
        spec = importlib.util.spec_from_file_location("xmdms_priv", path)
        if spec is None or spec.loader is None:
            raise ImportError("cannot load %s" % path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["xmdms_priv"] = module
        spec.loader.exec_module(module)
        install = getattr(module, "install", None)
        if not callable(install):
            raise RuntimeError("priv.py does not define install(window, app)")
        install(window, sys.modules[__name__])
    except Exception as error:
        traceback.print_exc()
        try:
            window._message("Private extension error: %s" % error)
        except Exception:
            pass


class QueryLogBus(QObject):
    record = Signal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = deque(maxlen=500)

    def add(self, header, payload):
        self.history.append((header, payload))
        self.record.emit(header, payload)


_query_bus = None


def query_log_bus():
    return _query_bus


def _log_payload(value):
    if isinstance(value, (bytes, bytearray)):
        if len(value) > 4000:
            return "<%d bytes>" % len(value)
        return bytes(value).decode("utf-8", "replace")
    return value


def install_query_logger():
    global _query_bus
    if _query_bus is None:
        _query_bus = QueryLogBus()
    if DVRIPCam is None:
        return
    if getattr(DVRIPCam.send, "_xm_query_wrapper", False):
        return
    underlying = DVRIPCam.send

    def send(self, *args, **kwargs):
        code = args[0] if args else kwargs.get("msg", kwargs.get("cmd_id"))
        body = args[1] if len(args) > 1 else kwargs.get("data")
        name = body.get("Name") if isinstance(body, dict) else ""
        label = (" %s" % name) if name else ""
        _query_bus.add("→ %s%s" % (code, label), _log_payload(body))
        reply = underlying(self, *args, **kwargs)
        _query_bus.add("← %s%s" % (code, label), _log_payload(reply))
        return reply

    send._xm_query_wrapper = True
    send._xm_query_underlying = underlying
    DVRIPCam.send = send


def uninstall_query_logger():
    if DVRIPCam is None:
        return
    current = DVRIPCam.send
    if getattr(current, "_xm_query_wrapper", False):
        DVRIPCam.send = current._xm_query_underlying


def parse_header(data):
    if len(data) < 20 or data[0] != 0xFF:
        return None
    return {
        "response": data[1] == 0x01,
        "session": int.from_bytes(data[4:8], "little"),
        "sequence": int.from_bytes(data[8:12], "little"),
        "total": data[12],
        "current": data[13],
        "msg_id": int.from_bytes(data[14:16], "little"),
        "length": int.from_bytes(data[16:20], "little"),
    }


def format_ipv4(value):
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    try:
        if text.lower().startswith("0x"):
            number = int(text, 16)
        elif text.isdigit():
            number = int(text)
        else:
            return text
    except ValueError:
        return text
    number &= 0xFFFFFFFF
    return ".".join(str((number >> (8 * index)) & 0xFF) for index in range(4))


def ip_sort_key(address):
    try:
        parts = [int(part) for part in str(address).split(".")]
        if len(parts) == 4:
            return tuple(parts)
    except ValueError:
        pass
    return (999, 999, 999, 999)


def sofia_hash(password):
    digest = hashlib.md5(password.encode("utf-8")).digest()
    return "".join(SOFIA_ALPHABET[sum(pair) % 62] for pair in zip(digest[::2], digest[1::2]))


def format_ip_set(address):
    return "0x%08X" % int.from_bytes(socket.inet_aton(address), "little")


def next_ip_address(value):
    text = str(value or "").strip()
    if not text or text == "0.0.0.0":
        return ""
    try:
        number = int(ipaddress.IPv4Address(text))
    except (ipaddress.AddressValueError, ValueError):
        return ""
    if number >= 0xFFFFFFFF:
        return ""
    return str(ipaddress.IPv4Address(number + 1))


def build_port_edit(value):
    edit = QLineEdit(str(value))
    edit.setValidator(QIntValidator(1, 65535, edit))
    return edit


def port_value(edit, default):
    try:
        return int(edit.text().strip())
    except (TypeError, ValueError):
        return default


LOGIN_PASSWORD_CODES = {
    106: "wrong username or password",
    203: "wrong password",
}


CONNECTION_ERROR_HINTS = (
    "cannot connect", "login failed", "connection reset", "connection aborted",
    "connection refused", "broken pipe", "timed out", "timeout", "socket",
    "closed", "eof", "not connected", "nonetype",
)

PASSWORD_FIELD_PROPERTY = "xmdms_password_field"


def passwords_visible():
    """Whether password fields are shown as plain text (default: shown)."""
    return QSettings("xmdm3", "xmdms").value(
        "show_passwords", True, type=bool)


def configure_password_edit(edit):
    """Mark a QLineEdit as a password field and apply the current mode."""
    edit.setProperty(PASSWORD_FIELD_PROPERTY, True)
    edit.setEchoMode(
        QLineEdit.EchoMode.Normal if passwords_visible()
        else QLineEdit.EchoMode.Password)
    return edit


def apply_password_visibility(visible=None):
    """Update every known password field, including open dialogs."""
    if visible is None:
        visible = passwords_visible()
    mode = (QLineEdit.EchoMode.Normal if visible
            else QLineEdit.EchoMode.Password)
    for widget in QApplication.allWidgets():
        if (isinstance(widget, QLineEdit)
                and bool(widget.property(PASSWORD_FIELD_PROPERTY))):
            widget.setEchoMode(mode)


I18N_SOURCE_ROLE = Qt.ItemDataRole.UserRole + 120
I18N_LAST_ROLE = Qt.ItemDataRole.UserRole + 121


def _translate_property(obj, prefix, current, setter):
    if not isinstance(current, str) or not current:
        return
    source_key = prefix + "_source"
    last_key = prefix + "_last"
    source = obj.property(source_key)
    last = obj.property(last_key)
    if not isinstance(source, str) or (isinstance(last, str)
                                       and current != last):
        source = current
        obj.setProperty(source_key, source)
    translated = tr(source)
    obj.setProperty(last_key, translated)
    if current != translated:
        setter(translated)


def _translate_table_header(item):
    current = item.text()
    source = item.data(I18N_SOURCE_ROLE)
    last = item.data(I18N_LAST_ROLE)
    if not isinstance(source, str) or (isinstance(last, str)
                                       and current != last):
        source = current
        item.setData(I18N_SOURCE_ROLE, source)
    translated = tr(source)
    item.setData(I18N_LAST_ROLE, translated)
    if current != translated:
        item.setText(translated)


def _translate_tabs(tabs):
    sources = tabs.property("_i18n_tabs_sources")
    if not isinstance(sources, list) or len(sources) != tabs.count():
        sources = [tabs.tabText(index) for index in range(tabs.count())]
        tabs.setProperty("_i18n_tabs_sources", sources)
    for index, source in enumerate(sources):
        translated = tr(str(source))
        if tabs.tabText(index) != translated:
            tabs.setTabText(index, translated)


def retranslate_widgets(root):
    """Translate static widget texts, keeping English source strings."""
    if root is None:
        return
    widgets = []
    if isinstance(root, QWidget):
        widgets.append(root)
    if hasattr(root, "findChildren"):
        widgets.extend(root.findChildren(QWidget))
    for widget in widgets:
        if isinstance(widget, QLabel) and not widget.property("i18nDynamic"):
            _translate_property(
                widget, "_i18n_label", widget.text(), widget.setText)
        if isinstance(widget, QAbstractButton):
            _translate_property(
                widget, "_i18n_button", widget.text(), widget.setText)
        if isinstance(widget, QGroupBox):
            _translate_property(
                widget, "_i18n_group", widget.title(), widget.setTitle)
        if isinstance(widget, QTabWidget):
            _translate_tabs(widget)
        if isinstance(widget, QTableWidget):
            for column in range(widget.columnCount()):
                item = widget.horizontalHeaderItem(column)
                if item is not None:
                    _translate_table_header(item)
        if isinstance(widget, QLineEdit):
            _translate_property(
                widget, "_i18n_placeholder",
                widget.placeholderText(), widget.setPlaceholderText)
        if isinstance(widget, QMenu):
            for action in widget.actions():
                _translate_property(
                    action, "_i18n_action", action.text(), action.setText)
        _translate_property(
            widget, "_i18n_tooltip", widget.toolTip(), widget.setToolTip)
        if widget.isWindow():
            _translate_property(
                widget, "_i18n_window",
                widget.windowTitle(), widget.setWindowTitle)


def retranslate_windows():
    for widget in QApplication.topLevelWidgets():
        if widget.isVisible():
            retranslate_widgets(widget)


class RetranslateFilter(QObject):
    def eventFilter(self, obj, event):
        if (event.type() == QEvent.Type.Show
                and isinstance(obj, QWidget)
                and (obj.isWindow() or isinstance(obj, QMenu))):
            retranslate_widgets(obj)
        return False

AUTH_ERROR_CODES = frozenset((106, 203, 204, 205))
TIMEOUT_ERROR_CODES = frozenset((108,))
AUTH_ERROR_HINTS = (
    "wrong password", "password is incorrect", "wrong username or password",
    "user is illegal", "user is locked",
)
TIMEOUT_ERROR_HINTS = (
    "timed out", "timeout", "no response", "unreachable", "cannot connect",
    "connection refused", "connection reset", "connection aborted",
    "broken pipe", "socket", "closed", "eof", "not connected",
)


def is_connection_error(text):
    """True when an error text means the NETIP socket/connection is gone."""
    lowered = str(text or "").lower()
    return any(hint in lowered for hint in CONNECTION_ERROR_HINTS)


def login_failure_text(camera):
    """Describe a failed NETIP login, flagging password errors explicitly."""
    code = getattr(camera, "session", None)
    if not isinstance(code, int):
        return "Login failed"
    if code in LOGIN_PASSWORD_CODES:
        return "Login failed — %s (Ret=%d)" % (LOGIN_PASSWORD_CODES[code], code)
    text = None
    if DVRIPCam is not None:
        codes = getattr(DVRIPCam, "CODES", None)
        if isinstance(codes, dict):
            text = codes.get(code)
    if text:
        return "Login failed: %s (Ret=%d)" % (text, code)
    return "Login failed"


UIMAGE_MAGIC = 0x27051956
UIMAGE_HEADER_SIZE = 64
DUMP_SIZE_STEPS = (8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096)


def parse_uimage_header(data):
    """Parse a U-Boot uImage header; None when the blob is not a uImage."""
    if not data or len(data) < UIMAGE_HEADER_SIZE:
        return None
    (magic, _hcrc, timestamp, size, load, entry,
     _dcrc) = struct.unpack(">IIIIIII", bytes(data[:28]))
    if magic != UIMAGE_MAGIC:
        return None
    name = bytes(data[32:64]).split(b"\x00", 1)[0].decode(
        "ascii", "replace").strip()
    return {
        "size": int(size),
        "load": int(load),
        "entry": int(entry),
        "timestamp": int(timestamp),
        "os": int(data[28]),
        "arch": int(data[29]),
        "type": int(data[30]),
        "comp": int(data[31]),
        "name": name,
    }


def tcp_reachable(address, port, timeout=3.0):
    """Fast TCP reachability probe.

    dvrip's connect() applies its timeout only after the blocking connect()
    call, so unreachable hosts can stall for minutes; probe first.
    """
    if not address:
        return False
    try:
        with socket.create_connection(
                (address, int(port or 34567)), timeout=timeout):
            return True
    except OSError:
        return False


def table_cell_text(table, index):
    """Displayed value of a table cell (item, cell widget or model data)."""
    if index is None or not index.isValid():
        return ""
    widget = table.indexWidget(index)
    if widget is not None:
        if hasattr(widget, "currentText"):
            return str(widget.currentText())
        if hasattr(widget, "text"):
            return str(widget.text())
    if hasattr(table, "item"):
        item = table.item(index.row(), index.column())
        if item is not None:
            if item.text():
                return item.text()
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                return "1" if item.checkState() == Qt.CheckState.Checked else "0"
            return ""
    value = table.model().data(index, Qt.ItemDataRole.DisplayRole)
    if value in (None, ""):
        state = table.model().data(index, Qt.ItemDataRole.CheckStateRole)
        if state is not None:
            return "1" if Qt.CheckState(state) == Qt.CheckState.Checked else "0"
    return "" if value is None else str(value)


def install_copy_menu(table, label="Copy"):
    """Add a context menu that copies the clicked cell's value."""
    table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def show_menu(point):
        index = table.indexAt(point)
        if not index.isValid():
            return
        text = table_cell_text(table, index)
        menu = QMenu(table)
        action = menu.addAction(label)
        action.setEnabled(bool(text))
        action.triggered.connect(
            lambda: QApplication.clipboard().setText(text))
        menu.exec(table.viewport().mapToGlobal(point))

    table.customContextMenuRequested.connect(show_menu)


def default_route_source_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("1.1.1.1", 53))
        return sock.getsockname()[0]
    except OSError:
        return ""
    finally:
        sock.close()


def parse_json_payload(data):
    header = parse_header(data)
    if header is None:
        return None, None
    if header["length"] and header["length"] <= len(data) - 20:
        payload = data[20:20 + header["length"]]
    else:
        payload = data[20:]
    text = payload.decode("utf-8", "replace").strip("\x00 \r\n\t")
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return header, None
    try:
        return header, json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return header, None


def parse_reply(data, source_ip):
    header, message = parse_json_payload(data)
    if header is None or message is None:
        return None
    common = message.get("NetWork.NetCommon")
    if not isinstance(common, dict):
        if any(key in message for key in ("HostIP", "MAC", "SN", "HostName")):
            common = message
        else:
            return None
    ip = format_ipv4(common.get("HostIP")) or source_ip
    return {
        "ip": ip,
        "mac": str(common.get("MAC") or ""),
        "sn": str(common.get("SN") or ""),
        "device_type": common.get("DeviceType"),
        "version": str(common.get("Version") or ""),
        "http_port": common.get("HttpPort"),
        "tcp_port": common.get("TCPPort"),
        "udp_port": common.get("UDPPort"),
        "host_name": str(common.get("HostName") or ""),
        "build_date": normalize_build_time(common.get("BuildDate")),
        "gateway": format_ipv4(common.get("GateWay")),
        "subnet": format_ipv4(common.get("Submask")),
        "source_ip": source_ip,
        "last_seen": time.time(),
        "raw": common,
    }


def build_ip_set_packet(device, address, submask, gateway, username, password, new_password,
                        http_port=None, tcp_port=None, host_name=None):
    raw = device.get("raw") or {}
    config = {}
    for field in SET_COPY_FIELDS:
        if field in raw:
            config[field] = raw[field]
    if http_port is not None:
        config["HttpPort"] = int(http_port)
    if tcp_port is not None:
        config["TCPPort"] = int(tcp_port)
    if host_name:
        config["HostName"] = host_name
    config["DvrMac"] = raw.get("MAC") or device.get("mac") or ""
    config["EncryptType"] = 1
    config["GateWay"] = format_ip_set(gateway)
    config["HostIP"] = format_ip_set(address)
    config["Submask"] = format_ip_set(submask)
    config["Username"] = username
    config["Password"] = sofia_hash(password)
    if new_password:
        config["NewPassWord"] = sofia_hash(new_password)
    body = json.dumps(
        config, ensure_ascii=False, sort_keys=True, separators=(", ", " : ")
    ).encode("utf-8") + b"\x0a\x00"
    header = bytearray(20)
    header[0] = 0xFF
    header[1] = 0x00
    header[2] = 0xFE
    header[14:16] = IP_SET_REQ.to_bytes(2, "little")
    header[16:20] = len(body).to_bytes(4, "little")
    return bytes(header) + body


def normalize_build_time(value):
    text = str(value or "").strip()
    if not text:
        return ""
    match = re.match(
        r"\s*(\d{4})\D+(\d{1,2})\D+(\d{1,2})"
        r"(?:\D+(\d{1,2})\D+(\d{1,2})(?:\D+(\d{1,2}))?)?", text)
    if not match:
        return text
    year, month, day = (int(match.group(index)) for index in (1, 2, 3))
    hour = int(match.group(4) or 0)
    minute = int(match.group(5) or 0)
    second = int(match.group(6) or 0)
    if not (1 <= month <= 12 and 1 <= day <= 31 and 0 <= hour <= 23
            and 0 <= minute <= 59 and 0 <= second <= 59):
        return text
    return "%04d-%02d-%02d %02d:%02d:%02d" % (
        year, month, day, hour, minute, second)


def format_device_age(build_time, now=None):
    try:
        built = datetime.strptime(
            normalize_build_time(build_time), "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return ""
    current = now or datetime.now()
    built_date = built.date()
    current_date = current.date()
    if built_date > current_date:
        return "0d"
    total = ((current_date.year - built_date.year) * 12
             + current_date.month - built_date.month)
    year = built_date.year + (built_date.month - 1 + total) // 12
    month = (built_date.month - 1 + total) % 12 + 1
    day = min(built_date.day, calendar.monthrange(year, month)[1])
    candidate = built_date.replace(year=year, month=month, day=day)
    if candidate > current_date:
        total -= 1
        year = built_date.year + (built_date.month - 1 + total) // 12
        month = (built_date.month - 1 + total) % 12 + 1
        day = min(built_date.day, calendar.monthrange(year, month)[1])
        candidate = built_date.replace(year=year, month=month, day=day)
    years, months = divmod(total, 12)
    days = (current_date - candidate).days
    if years < 0:
        years, months, days = 0, 0, 0
    parts = []
    if years:
        parts.append("%dy" % years)
    if months:
        parts.append("%dm" % months)
    parts.append("%dd" % days)
    return " ".join(parts)


def format_device_runtime(value):
    try:
        if isinstance(value, str):
            text = value.strip()
            minutes = int(text, 16) if text.lower().startswith("0x") else int(text)
        else:
            minutes = int(value)
    except (TypeError, ValueError):
        return ""
    if minutes < 0:
        return ""
    days, remainder = divmod(minutes, 1440)
    hours = remainder // 60
    years, days = divmod(days, 365)
    months, days = divmod(days, 30)
    parts = []
    if years:
        parts.append("%dy" % years)
    if months:
        parts.append("%dm" % months)
    if years or months or days:
        parts.append("%dd" % days)
    else:
        parts.append("%dh" % hours)
    return " ".join(parts)


def manual_device(address, port, username, password, cloud_id=None, rps=True):
    return {
        "ip": address,
        "cloud_id": cloud_id or "",
        "rps": bool(rps),
        "no_md5": False,
        "tcp_port": int(port) if port else 34567,
        "username": username or "admin",
        "password": password or "",
        "sn": "",
        "mac": "",
        "device_type": None,
        "version": "",
        "http_port": None,
        "udp_port": None,
        "host_name": "",
        "build_date": "",
        "gateway": "",
        "subnet": "",
        "source_ip": "",
        "last_seen": time.time(),
        "raw": {},
        "manual": True,
    }


def build_rtsp_url(device, username, password, channel, stream):
    user = quote(username or "", safe="")
    secret = quote(sofia_hash(password or ""), safe="")
    ip = device.get("ip") or ""
    return "rtsp://%s:%s@%s:554/user=%s_password=%s_channel=%d_stream=%d.sdp?real_stream" % (
        user, secret, ip, user, secret, channel, stream)


def build_snapshot_url(device, username, password, channel):
    user = quote(username or "", safe="")
    secret = quote(password or "", safe="")
    ip = device.get("ip") or ""
    return "http://%s:%s@%s/webcapture.jpg?command=snap&channel=%d" % (
        user, secret, ip, channel)


def devices_to_csv(devices):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["number", "ip", "mac", "sn", "version", "build_date", "host_name"])
    for index, device in enumerate(devices):
        writer.writerow([
            index + 1,
            device.get("ip") or "",
            device.get("mac") or "",
            device.get("sn") or "",
            device.get("version") or "",
            device.get("build_date") or "",
            device.get("host_name") or "",
        ])
    return buffer.getvalue()


def broadcast_address(ip, netmask):
    try:
        ip_value = struct.unpack("!I", socket.inet_aton(ip))[0]
        mask_value = struct.unpack("!I", socket.inet_aton(netmask))[0]
    except OSError:
        return "255.255.255.255"
    return socket.inet_ntoa(struct.pack("!I", ip_value | (~mask_value & 0xFFFFFFFF)))


def list_interfaces():
    interfaces = []
    default_ip = default_route_source_ip()
    if psutil is not None:
        try:
            addresses = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
        except Exception:
            addresses = {}
            stats = {}
        for name in sorted(addresses):
            stat = stats.get(name)
            if stat is not None and not stat.isup:
                continue
            for entry in addresses.get(name, []):
                if entry.family != socket.AF_INET or not entry.address:
                    continue
                if entry.address.startswith("127."):
                    continue
                interfaces.append({
                    "name": name,
                    "ip": entry.address,
                    "broadcast": broadcast_address(entry.address, entry.netmask) if entry.netmask else "255.255.255.255",
                    "default": bool(default_ip) and entry.address == default_ip,
                })
    interfaces.append({"name": "All interfaces", "ip": "", "broadcast": "255.255.255.255", "default": False})
    if not any(interface["default"] for interface in interfaces):
        interfaces[0]["default"] = True
    return interfaces


class DiscoveryThread(QThread):
    device_found = Signal(dict)
    status_changed = Signal(str)
    failed = Signal(str)

    def __init__(self, interface_ip, broadcast_ip, port=DISCOVERY_PORT,
                 duration=5.0, min_probes=3, parent=None):
        super().__init__(parent)
        self._interface_ip = interface_ip
        self._broadcast_ip = broadcast_ip
        self._port = port
        self._duration = max(0.1, float(duration))
        self._min_probes = max(1, int(min_probes))
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1 << 20)
            except OSError:
                pass
            targets = []
            for target in (self._broadcast_ip, "255.255.255.255"):
                if target and target != "0.0.0.0" and target not in targets:
                    targets.append(target)
            candidates = []
            for address in ("", self._interface_ip or ""):
                for port in (self._port, 0):
                    candidate = (address, port)
                    if candidate not in candidates:
                        candidates.append(candidate)
            bound = None
            last_error = None
            for candidate in candidates:
                try:
                    sock.bind(candidate)
                    bound = sock.getsockname()
                    break
                except OSError as error:
                    last_error = error
            if bound is None:
                self.failed.emit(f"Cannot bind UDP socket: {last_error}")
                return
            sock.settimeout(0.25)
            grace = min(1.0, self._duration / 3.0)
            span = max(0.0, self._duration - grace)
            if self._min_probes > 1:
                interval = min(PROBE_INTERVAL, span / (self._min_probes - 1))
            else:
                interval = min(PROBE_INTERVAL, span)
            interval = max(interval, 0.05)
            started = time.monotonic()
            probe_until = started + span
            deadline = started + self._duration
            self.status_changed.emit("Searching %.0fs on %s:%d via %s (probe every %.2fs)" % (
                self._duration, bound[0] or "0.0.0.0", bound[1], ", ".join(targets), interval))
            next_probe = started
            probes_sent = 0
            while not self._stop and time.monotonic() < deadline:
                now = time.monotonic()
                if now >= next_probe and (probes_sent < self._min_probes or now <= probe_until + 0.001):
                    for target in targets:
                        try:
                            sock.sendto(PROBE, (target, self._port))
                        except OSError:
                            pass
                    probes_sent += 1
                    next_probe = now + interval
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                try:
                    sock.settimeout(min(0.25, max(0.01, remaining)))
                    data, address = sock.recvfrom(65535)
                except socket.timeout:
                    continue
                except OSError as error:
                    if not self._stop:
                        self.failed.emit(str(error))
                    break
                device = parse_reply(data, address[0])
                if device is not None:
                    self.device_found.emit(device)
        finally:
            sock.close()


class ProbeThread(QThread):
    device_found = Signal(dict)
    failed = Signal(str)

    def __init__(self, target_ip, interface_ip="", port=DISCOVERY_PORT, timeout=2.5, parent=None):
        super().__init__(parent)
        self._target_ip = target_ip
        self._interface_ip = interface_ip
        self._port = port
        self._timeout = timeout

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1 << 20)
            except OSError:
                pass
            candidates = []
            for address in ("", self._interface_ip or ""):
                for port in (self._port, 0):
                    candidate = (address, port)
                    if candidate not in candidates:
                        candidates.append(candidate)
            bound = None
            last_error = None
            for candidate in candidates:
                try:
                    sock.bind(candidate)
                    bound = sock.getsockname()
                    break
                except OSError as error:
                    last_error = error
            if bound is None:
                self.failed.emit("Cannot bind UDP socket: %s" % last_error)
                return
            sock.settimeout(0.25)
            deadline = time.monotonic() + self._timeout
            next_probe = 0.0
            while time.monotonic() < deadline:
                now = time.monotonic()
                if now >= next_probe:
                    try:
                        sock.sendto(PROBE, (self._target_ip, self._port))
                    except OSError:
                        pass
                    next_probe = now + 0.5
                try:
                    data, address = sock.recvfrom(65535)
                except socket.timeout:
                    continue
                except OSError as error:
                    self.failed.emit(str(error))
                    return
                device = parse_reply(data, address[0])
                if device is not None and address[0] == self._target_ip:
                    self.device_found.emit(device)
                    return
            self.failed.emit("No reply from %s" % self._target_ip)
        finally:
            sock.close()


class IpSetThread(QThread):
    result = Signal(dict)
    failed = Signal(str)

    def __init__(self, device, address, submask, gateway, username, password, new_password,
                 interface_ip, broadcast_ip, http_port=None, tcp_port=None, host_name=None,
                 port=DISCOVERY_PORT, timeout=SET_TIMEOUT, parent=None):
        super().__init__(parent)
        self._packet = build_ip_set_packet(
            device, address, submask, gateway, username, password, new_password,
            http_port=http_port, tcp_port=tcp_port, host_name=host_name)
        self._interface_ip = interface_ip
        self._broadcast_ip = broadcast_ip
        self._port = port
        self._timeout = timeout

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1 << 20)
            except OSError:
                pass
            candidates = []
            for address in ("", self._interface_ip or ""):
                for port in (self._port, 0):
                    candidate = (address, port)
                    if candidate not in candidates:
                        candidates.append(candidate)
            bound = None
            last_error = None
            for candidate in candidates:
                try:
                    sock.bind(candidate)
                    bound = sock.getsockname()
                    break
                except OSError as error:
                    last_error = error
            if bound is None:
                self.failed.emit("Cannot bind UDP socket: %s" % last_error)
                return
            sock.settimeout(0.25)
            targets = []
            for target in (self._broadcast_ip, "255.255.255.255"):
                if target and target != "0.0.0.0" and target not in targets:
                    targets.append(target)
            for target in targets:
                try:
                    sock.sendto(self._packet, (target, self._port))
                except OSError:
                    pass
            deadline = time.monotonic() + self._timeout
            while time.monotonic() < deadline:
                try:
                    data, address = sock.recvfrom(65535)
                except socket.timeout:
                    continue
                except OSError as error:
                    self.failed.emit(str(error))
                    return
                header, message = parse_json_payload(data)
                if header is None or message is None:
                    continue
                if header["msg_id"] == IP_SET_RSP:
                    self.result.emit(message)
                    return
            self.failed.emit("No response from the device (timeout)")
        finally:
            sock.close()


class NetipThread(QThread):
    fetched = Signal(dict)
    applied = Signal(dict)
    failed = Signal(str)
    progress = Signal(str)
    connected = Signal(str)

    def __init__(self, action, address, username, password, cloud_id=None,
                 rps=True, changes=None, port=34567, timeout=8.0, parent=None,
                 no_md5=False):
        super().__init__(parent)
        self._action = action
        self._address = address
        self._username = username
        self._password = password
        self._no_md5 = bool(no_md5)
        self._cloud_id = cloud_id or ""
        self._rps = bool(rps)
        self._changes = changes or {}
        self._port = int(port or 34567)
        self._timeout = timeout
        self._camera = None
        self._cancelled = False

    def cancel(self):
        self._cancelled = True
        camera = self._camera
        if camera is not None:
            try:
                camera.close()
            except Exception:
                pass

    def run(self):
        if DVRIPCam is None:
            self.failed.emit("python-dvr (dvrip.py) is not available")
            return
        camera = None
        try:
            address = self._cloud_id or self._address
            camera = DVRIPCam(address, user=self._username,
                              password=self._password, port=self._port)
            if self._no_md5:
                camera.hash_pass = self._password
            self._camera = camera
            if self._cloud_id:
                load_cloud_patch()
                if self._rps:
                    os.environ["RPS"] = "1"
                else:
                    os.environ.pop("RPS", None)
                camera._cloud_device = True
            if not self._cloud_id and not tcp_reachable(self._address, self._port):
                if not self._cancelled:
                    self.failed.emit("Cannot connect to %s:%s (unreachable)" % (
                        self._address, self._port))
                return
            camera.connect(timeout=self._timeout)
            if self._cancelled:
                return
            if not camera.login():
                if not self._cancelled:
                    self.failed.emit(login_failure_text(camera))
                return
            if not self._cancelled:
                self.connected.emit(self._cloud_id or self._address)
            action = self._action
            if action == "fetch":
                keys = self._changes.get("keys")
                keys = set(keys) if keys else None

                def want(name):
                    return keys is None or name in keys

                payload = {}

                def read(name, label, source=None, command=None, code=1042):
                    if not want(name):
                        return None
                    self.progress.emit("Fetching %s" % label)
                    try:
                        if source is not None:
                            value = source()
                        else:
                            value = camera.get_command(command, code)
                    except Exception:
                        value = None
                    payload[name] = value
                    return value

                loop_keys = ("encode_channels", "encode_smart", "encode_ability",
                             "camera_param", "camera_ex_param", "white_light")
                need_loop = any(want(name) for name in loop_keys)
                need_channels = want("chn_status") or need_loop
                system_info = None
                if want("system") or need_channels:
                    if want("system"):
                        system_info = read("system", "SystemInfo",
                                           source=camera.get_system_info)
                    else:
                        self.progress.emit("Fetching SystemInfo")
                        try:
                            system_info = camera.get_system_info()
                        except Exception:
                            system_info = None
                chn_status = []
                dig_channels = 0
                if need_channels:
                    if want("chn_status"):
                        chn_status = read(
                            "chn_status", "NetWork.ChnStatus",
                            source=lambda: self._read_list(
                                camera, "NetWork.ChnStatus", 1042)) or []
                    else:
                        self.progress.emit("Fetching NetWork.ChnStatus")
                        chn_status = self._read_list(
                            camera, "NetWork.ChnStatus", 1042)
                    try:
                        dig_channels = int((system_info or {}).get("DigChannel") or 0)
                    except (AttributeError, TypeError, ValueError):
                        dig_channels = 0
                if need_loop:
                    smart_v1 = []
                    smart_v2 = []
                    if want("encode_smart"):
                        smart_v1 = self._read_list(
                            camera, "ChannelSystemFunction@SmartH264.[0]]", 1362)
                        smart_v2 = self._read_list(
                            camera, "ChannelSystemFunction@SmartH264V2.[0]", 1362)
                    encode_channels = []
                    encode_smart = []
                    encode_ability = []
                    camera_param = []
                    camera_ex_param = []
                    white_light = []
                    for chn in range(dig_channels):
                        status = chn_status[chn] if chn < len(chn_status) else None
                        connected = (isinstance(status, dict)
                                     and status.get("Status") == "Connected")
                        if not connected:
                            encode_channels.append(None)
                            encode_smart.append(None)
                            encode_ability.append(None)
                            camera_param.append(None)
                            camera_ex_param.append(None)
                            white_light.append(None)
                            continue
                        if want("encode_channels"):
                            encode_channels.append(self._read_encode(
                                camera, "NetUse.DigitalEncode.[%d]" % chn))
                        if want("encode_ability"):
                            try:
                                self.progress.emit(
                                    "Fetching NetUse.DigitalAbility.[%d]" % chn)
                                encode_ability.append(camera.get_command(
                                    "NetUse.DigitalAbility.[%d]" % chn, 1042))
                            except Exception:
                                encode_ability.append(None)
                        if want("camera_param"):
                            try:
                                self.progress.emit(
                                    "Fetching Camera.Param.[%d]" % chn)
                                camera_param.append(camera.get_command(
                                    "Camera.Param.[%d]" % chn, 1042))
                            except Exception:
                                camera_param.append(None)
                        if want("camera_ex_param"):
                            try:
                                self.progress.emit(
                                    "Fetching Camera.ParamEx.[%d]" % chn)
                                camera_ex_param.append(camera.get_command(
                                    "Camera.ParamEx.[%d]" % chn, 1042))
                            except Exception:
                                camera_ex_param.append(None)
                        if want("white_light"):
                            try:
                                self.progress.emit(
                                    "Fetching Camera.WhiteLight.[%d]" % chn)
                                white_light.append(camera.get_command(
                                    "Camera.WhiteLight.[%d]" % chn, 1042))
                            except Exception:
                                white_light.append(None)
                        if want("encode_smart"):
                            has_v2 = chn < len(smart_v2) and smart_v2[chn] == 1
                            has_v1 = chn < len(smart_v1) and smart_v1[chn] == 1
                            if has_v2 and has_v1:
                                self.progress.emit(
                                    "Fetching AVEnc.SmartH264V2.[%d]" % chn)
                                encode_smart.append({
                                    "mode": "v2",
                                    "config": camera.get_command(
                                        "AVEnc.SmartH264V2.[%d]" % chn, 1042)})
                            elif has_v1:
                                self.progress.emit(
                                    "Fetching AVEnc.SmartH264.[%d]" % chn)
                                encode_smart.append({
                                    "mode": "v1",
                                    "config": camera.get_command(
                                        "AVEnc.SmartH264.[%d]" % chn, 1042)})
                            else:
                                encode_smart.append(None)
                    if not dig_channels:
                        if want("encode_ability"):
                            try:
                                self.progress.emit("Fetching EncodeCapability")
                                reply = camera.get_command("EncodeCapability", 1360)
                                if (isinstance(reply, dict)
                                        and reply.get("Ret") in (None, 100)):
                                    encode_ability = [reply]
                            except Exception:
                                encode_ability = []
                        if want("camera_param"):
                            try:
                                camera_param = [camera.get_command(
                                    "Camera.Param.[0]", 1042)]
                            except Exception:
                                camera_param = [None]
                        if want("camera_ex_param"):
                            try:
                                camera_ex_param = [camera.get_command(
                                    "Camera.ParamEx.[0]", 1042)]
                            except Exception:
                                camera_ex_param = [None]
                        if want("white_light"):
                            try:
                                white_light = [camera.get_command(
                                    "Camera.WhiteLight", 1042)]
                            except Exception:
                                white_light = [None]
                        if want("encode_smart"):
                            has_v2 = bool(smart_v2) and smart_v2[0] == 1
                            has_v1 = bool(smart_v1) and smart_v1[0] == 1
                            if has_v2 and has_v1:
                                encode_smart.append({
                                    "mode": "v2",
                                    "config": camera.get_command(
                                        "AVEnc.SmartH264V2.[0]", 1042)})
                            elif has_v1:
                                encode_smart.append({
                                    "mode": "v1",
                                    "config": camera.get_command(
                                        "AVEnc.SmartH264.[0]", 1042)})
                            else:
                                encode_smart.append(None)
                    if want("encode_channels"):
                        payload["encode_channels"] = encode_channels
                    if want("encode_smart"):
                        payload["encode_smart"] = encode_smart
                    if want("encode_ability"):
                        payload["encode_ability"] = encode_ability
                    if want("camera_param"):
                        payload["camera_param"] = camera_param
                    if want("camera_ex_param"):
                        payload["camera_ex_param"] = camera_ex_param
                    if want("white_light"):
                        payload["white_light"] = white_light
                for name, command, code in (
                        ("common", "NetWork.NetCommon", 1042),
                        ("dhcp", "NetWork.NetDHCP", 1042),
                        ("adaptive", "NetWork.IPAdaptive", 1042),
                        ("dns", "NetWork.NetDNS", 1042),
                        ("smartnet", "NetWork.SmartNetAutoConnect", 1042),
                        ("wifi", "NetWork.Wifi", 1042),
                        ("rtsp", "NetWork.RTSP", 1042),
                        ("online_upgrade", "NetWork.OnlineUpgrade", 1042),
                        ("upnp", "NetWork.Upnp", 1042),
                        ("onvif_pwd", "NetWork.OnvifPwdCheckout", 1042),
                        ("pms", "NetWork.PMS", 1042),
                        ("ntp", "NetWork.NetNTP", 1042),
                        ("pubcfg", "NetWork.NetPubCfgDomain", 1042),
                        ("caps", "NetWork.NetCapsDomain", 1042),
                        ("force_dhcp", "NetWork.ForceNetDHCP", 1042),
                        ("disable_xm_server", "NetWork.DisableXmServerConn", 1042),
                        ("nat", "NetWork.Nat", 1042),
                        ("ability", "Ability.FunctionEnable", 1042),
                        ("device_desc", "Ability.DeviceDesc", 1042),
                        ("max_preview", "fVideo.MaxPreviewNum", 1042),
                        ("system_timezone", "System.TimeZone", 1042),
                        ("nat_info", "Status.NatInfo", 1042),
                        ("video_out", "fVideo.VideoOut", 1042),
                        ("gui_set", "fVideo.GUISet", 1042),
                        ("vga_resolution", "Ability.VGAResolution", 1042),
                        ("general", "General", 1042),
                        ("storage_info", "StorageInfo", 1020),
                        ("oemcfg", "OEMcfg.Correspondent", 1042),
                        ("uart_comm", "Uart.Comm", 1042),
                        ("uart_ptz", "Uart.PTZ", 1042),
                        ("uart_rs485", "Uart.RS485", 1042),
                        ("com_protocol", "ComProtocol", 1360),
                        ("ptz_protocol", "PTZProtocol", 1360),
                        ("uart_protocol", "UartProtocol", 1360)):
                    read(name, command, command=command, code=code)
                read("languages", "MultiLanguage", command="MultiLanguage", code=1360)
                read("users", "GetAllUser",
                     source=lambda: camera.send(1472, {"Name": "GetAllUser"}))
                read("groups", "GetAllGroup",
                     source=lambda: camera.send(1474, {"Name": "GetAllGroup"}))
                read("authority_list", "GetFullAuthoritylist",
                     source=lambda: camera.send(1470, {"Name": "GetFullAuthoritylist"}))
                read("av_encode", "Simplify.Encode",
                     source=lambda: None if dig_channels else camera.get_command(
                         "Simplify.Encode", 1042))
                self.fetched.emit(payload)
                return
            if action == "apply":
                self.applied.emit(self._apply_general(camera, self._changes))
                return
            if action == "network_config":
                self.applied.emit(self._apply_network_config(camera, self._changes))
                return
            if action == "upgrade":
                filename = self._changes.get("filename") or ""
                if not filename:
                    self.failed.emit("No firmware file selected")
                    return
                result = camera.upgrade(
                    filename,
                    vprint=lambda *args, **kwargs: self.progress.emit(
                        " ".join(str(arg) for arg in args)))
                self.applied.emit({"Upgrade": result})
                return
            if action == "cloud_upgrade_list":
                self.fetched.emit({
                    "version_list": camera.send(2000, {"Name": "OPVersionList"}),
                })
                return
            if action == "cloud_upgrade_apply":
                self.applied.emit({
                    "OPReqVersion": camera.send(
                        2002, {"Name": "OPReqVersion",
                               "OPReqVersion": self._changes.get("version")}),
                })
                return
            if action == "logs":
                end = datetime.now()
                begin = end - timedelta(days=30)
                self.fetched.emit({"logs": camera.send(1442, {
                    "Name": "OPLogQuery",
                    "OPLogQuery": {
                        "BeginTime": begin.strftime("%Y-%m-%d %H:%M:%S"),
                        "EndTime": end.strftime("%Y-%m-%d %H:%M:%S"),
                        "LogPosition": 0,
                        "Type": "LogAll",
                    },
                })})
                return
            if action == "erase_logs":
                self.applied.emit({"EraseLogs": camera.send(1450, {
                    "Name": "OPLogManager", "OPLogManager": {"Action": "RemoveAll"}})})
                return
            if action == "reset_config":
                self.applied.emit({"OPDefaultConfig": camera.send(1450, {
                    "Name": "OPDefaultConfig",
                    "OPDefaultConfig": self._changes.get("config") or {}})})
                return
            if action == "sync_time":
                self.applied.emit({"SyncTime": camera.set_time()})
                return
            if action == "remote_devices":
                self.fetched.emit({
                    "remote_devices": camera.get_command("NetWork.RemoteDeviceV3", 1042),
                    "channel_titles": self._read_list(camera, "ChannelTitle", 1048),
                    "time_syn": self._read_list(camera, "NetWork.DigTimeSyn", 1042),
                    "decode_param": self._read_list(camera, "Media.DecodeParam", 1042),
                })
                return
            if action == "set_remote_devices":
                changes = self._changes
                results = {
                    "RemoteDeviceV3": camera.set_command(
                        "NetWork.RemoteDeviceV3", changes.get("channels") or [], 1040),
                }
                if changes.get("titles") is not None:
                    results["ChannelTitle"] = camera.set_command(
                        "ChannelTitle", changes["titles"], 1046)
                if changes.get("time_syn") is not None:
                    results["NetWork.DigTimeSyn"] = camera.set_command(
                        "NetWork.DigTimeSyn", changes["time_syn"], 1040)
                if changes.get("decode_param") is not None:
                    results["Media.DecodeParam"] = camera.set_command(
                        "Media.DecodeParam", changes["decode_param"], 1040)
                self.applied.emit(results)
                return
            if action == "wifi_scan":
                self.fetched.emit({
                    "wifi_scan": camera.get_command("WifiAP", 1020)})
                return
            if action == "dig_set_ip":
                reply = camera.send(1652, self._changes.get("payload") or {})
                self.applied.emit({"OPDIGSetIP": reply})
                return
            if action == "snapshot":
                channel = int(self._changes.get("channel") or 0)
                self.fetched.emit({"snapshot": camera.snapshot(channel=channel)})
                return
            if action == "local_search":
                protocol = str(self._changes.get("protocol") or "NETIP").upper()
                if protocol == "ONVIF":
                    reply = camera.send(1634, {
                        "Name": "NetLocalSearch",
                        "OPLocalSearch": {"SearchProtocol": "ONVIF"}})
                else:
                    reply = camera.get_command("NetLocalSearch", 1634)
                devices = reply.get("OPLocalSearch", reply.get("NetLocalSearch", [])) \
                    if isinstance(reply, dict) else reply
                self.fetched.emit({"local_search": devices})
                return
            if action == "users_info":
                self.fetched.emit({
                    "users": camera.send(1472, {"Name": "GetAllUser"}),
                    "groups": camera.send(1474, {"Name": "GetAllGroup"}),
                    "authority_list": camera.send(
                        1470, {"Name": "GetFullAuthoritylist"})})
                return
            if action in ("user_add", "user_modify", "user_delete", "user_password",
                          "group_add", "group_modify", "group_delete"):
                values = self._changes.get("values") or {}
                if action == "user_delete":
                    reply = camera.send(1486, {"Name": values.get("name")})
                elif action == "user_password":
                    reply = camera.send(1488, {
                        "EncryptType": "NONE",
                        "UserName": values.get("name"),
                        "PassWord": values.get("old") or "",
                        "NewPassWord": values.get("new") or ""})
                elif action == "group_delete":
                    reply = camera.send(1480, {"Name": values.get("name")})
                elif action in ("group_add", "group_modify"):
                    group = {
                        "Name": values.get("name"),
                        "Memo": values.get("memo") or "",
                        "AuthorityList": values.get("authority") or [],
                    }
                    if action == "group_add":
                        reply = camera.send(1476, {"Name": "AddGroup", "Group": group})
                    else:
                        reply = camera.send(1478, {
                            "Name": "ModifyGroup", "Group": group,
                            "GroupName": self._changes.get("original")
                            or values.get("name")})
                else:
                    user = dict(self._changes.get("user") or {})
                    user.update({
                        "Name": values.get("name"),
                        "Group": values.get("group"),
                        "Memo": values.get("memo") or "",
                        "Sharable": bool(values.get("sharable")),
                        "AuthorityList": values.get("authority")
                        or user.get("AuthorityList") or [],
                    })
                    if action == "user_add":
                        user["Password"] = values.get("password") or ""
                        user["Reserved"] = False
                        reply = camera.send(1482, {
                            "Name": "AddUser", "EncryptType": "NONE", "User": user})
                    else:
                        reply = camera.send(1484, {
                            "Name": "ModifyUser", "User": user,
                            "UserName": self._changes.get("original")
                            or values.get("name")})
                results = {action: reply}
                if isinstance(reply, dict) and reply.get("Ret") == 100:
                    try:
                        results["users"] = camera.send(1472, {"Name": "GetAllUser"})
                        results["groups"] = camera.send(1474, {"Name": "GetAllGroup"})
                    except Exception:
                        pass
                self.applied.emit(results)
                return
            if action == "config_export":
                self.applied.emit({
                    "config_export": camera.send(1542, {"Name": "GetConfig"})})
                return
            if action == "config_import":
                data = self._changes.get("data") or b""
                if isinstance(data, str):
                    data = base64.b64decode(data)
                data = bytes(data)
                reply = camera.set_command(
                    "OPSystemUpgrade", {"Action": "Start", "Type": "Config"}, 0x5F0)
                if not isinstance(reply, dict) or reply.get("Ret") not in camera.OK_CODES:
                    self.applied.emit({"config_import": reply})
                    return
                packetsize = 0x8000
                blocknum = 0
                rcvd = bytearray()
                for offset in range(0, len(data), packetsize):
                    chunk = data[offset:offset + packetsize]
                    header = struct.pack("BB2xII2xHI", 255, 0, camera.session,
                                         blocknum, 0x5F2, len(chunk))
                    camera.socket_send(header + chunk)
                    blocknum += 1
                    self.progress.emit("Importing config %d%%" % int(
                        min(offset + len(chunk), len(data)) * 100 / max(1, len(data))))
                    reply, rcvd = camera.recv_json(rcvd)
                    if reply and reply.get("Ret") != 100:
                        self.applied.emit({"config_import": reply})
                        return
                end = struct.pack("BB2xIIxBHI", 255, 0, camera.session, blocknum, 1,
                                  0x05F2, 0)
                camera.socket_send(end)
                final = None
                try:
                    final, rcvd = camera.recv_json(rcvd)
                except Exception:
                    final = None
                self.applied.emit({"config_import": final or {"Ret": 100}})
                return
            if action == "storage_info":
                self.fetched.emit({
                    "storage_info": camera.get_command("StorageInfo", 1020)})
                return
            if action == "storage_action":
                result = camera.send(1460, {
                    "Name": "OPStorageManager",
                    "OPStorageManager": self._changes.get("payload") or {}})
                results = {"OPStorageManager": result}
                if isinstance(result, dict) and result.get("Ret") == 100:
                    try:
                        results["storage_info"] = camera.get_command("StorageInfo", 1020)
                    except Exception:
                        pass
                self.applied.emit(results)
                return
            if action == "reboot":
                camera.reboot()
                self.applied.emit({"Reboot": {"Ret": 100}})
                return
            self.failed.emit("Unknown action: %s" % action)
        except Exception as error:
            if not self._cancelled:
                self.failed.emit("%s: %s" % (type(error).__name__, error))
        finally:
            if camera is not None:
                try:
                    camera.close()
                except Exception:
                    pass

    @staticmethod
    def _read_list(camera, command, code):
        try:
            reply = camera.get_command(command, code)
        except Exception:
            return []
        if isinstance(reply, list):
            return reply
        if isinstance(reply, dict):
            for value in reply.values():
                if isinstance(value, list):
                    return value
        return []

    @staticmethod
    def _read_encode(camera, command):
        try:
            reply = camera.get_command(command, 1042)
        except Exception:
            return None
        if isinstance(reply, list):
            return reply
        if isinstance(reply, dict) and "Ret" not in reply:
            for value in reply.values():
                if isinstance(value, list):
                    return value
        return None

    def _apply_network_config(self, camera, changes):
        results = {}
        dns = changes.get("dns")
        if dns:
            results["NetWork.NetDNS"] = camera.set_command("NetWork.NetDNS", dns, 1040)
        dhcp = changes.get("dhcp")
        if dhcp:
            results["NetWork.NetDHCP"] = camera.set_command("NetWork.NetDHCP", dhcp, 1040)
        adaptive = changes.get("adaptive")
        if adaptive:
            results["NetWork.IPAdaptive"] = camera.set_command(
                "NetWork.IPAdaptive", adaptive, 1040)
        smartnet = changes.get("smartnet")
        if smartnet:
            results["NetWork.SmartNetAutoConnect"] = camera.set_command(
                "NetWork.SmartNetAutoConnect", smartnet, 1040)
        wifi = changes.get("wifi")
        if wifi:
            results["NetWork.Wifi"] = camera.set_command("NetWork.Wifi", wifi, 1040)
        rtsp = changes.get("rtsp")
        if rtsp:
            results["NetWork.RTSP"] = camera.set_command("NetWork.RTSP", rtsp, 1040)
        upgrade = changes.get("upgrade")
        if upgrade:
            results["NetWork.OnlineUpgrade"] = camera.set_command(
                "NetWork.OnlineUpgrade", upgrade, 1040)
        for key, command in (
                ("upnp", "NetWork.Upnp"),
                ("onvif_pwd", "NetWork.OnvifPwdCheckout"),
                ("pms", "NetWork.PMS"),
                ("ntp", "NetWork.NetNTP"),
                ("pubcfg", "NetWork.NetPubCfgDomain"),
                ("caps", "NetWork.NetCapsDomain"),
                ("force_dhcp", "NetWork.ForceNetDHCP"),
                ("disable_xm_server", "NetWork.DisableXmServerConn"),
                ("nat", "NetWork.Nat")):
            data = changes.get(key)
            if data:
                results[command] = camera.set_command(command, data, 1040)
        oemcfg = changes.get("oemcfg")
        if oemcfg:
            results["OEMcfg.Correspondent"] = camera.set_command(
                "OEMcfg.Correspondent", oemcfg, 1040)
        project = changes.get("project_mode")
        if project is not None:
            general = camera.get_command("General", 1042)
            if not isinstance(general, dict):
                general = {}
            general["ProjectMode"] = {"Enable": bool(project)}
            results["General"] = camera.set_command("General", general, 1040)
        return results

    def _apply_general(self, camera, changes):
        results = {}
        values = changes.get("values") or {}
        maintain = changes.get("maintain")
        if values or maintain:
            general = camera.get_command("General", 1042)
            if not isinstance(general, dict):
                general = {}
            keys = changes.get("keys") or {}
            location = general.get("Location")
            location = dict(location) if isinstance(location, dict) else {}
            for field, value in values.items():
                if value in (None, ""):
                    continue
                key = keys.get(field) or SYSTEM_GENERAL_KEYS.get(field, (field,))[0]
                if key in location:
                    location[key] = value
                else:
                    general[key] = value
            if location:
                general["Location"] = location
            if maintain:
                current = general.get("AutoMaintain")
                current = dict(current) if isinstance(current, dict) else {}
                current.update(maintain)
                general["AutoMaintain"] = current
            results["General"] = camera.set_command("General", general, 1040)
        timezone = changes.get("timezone")
        if timezone:
            results["System.TimeZone"] = camera.set_command(
                "System.TimeZone", timezone, 1040)
        device_desc = changes.get("device_desc")
        if device_desc:
            results["Ability.DeviceDesc"] = camera.set_command(
                "Ability.DeviceDesc", device_desc, 1040)
        preview_num = changes.get("preview_num")
        if preview_num is not None:
            reply = camera.set_command(
                "fVideo.MaxPreviewNum", {"PreviewNum": preview_num}, 1040)
            if reply is None:
                time.sleep(2)
                try:
                    current = camera.get_command("fVideo.MaxPreviewNum", 1042)
                except Exception:
                    current = None
                if isinstance(current, dict) and current.get("PreviewNum") == preview_num:
                    reply = {"Ret": 100, "Confirmed": True}
            results["fVideo.MaxPreviewNum"] = reply
        video_out = changes.get("video_out")
        if video_out:
            results["fVideo.VideoOut"] = camera.set_command(
                "fVideo.VideoOut", video_out, 1040)
        gui_set = changes.get("gui_set")
        if gui_set:
            results["fVideo.GUISet"] = camera.set_command(
                "fVideo.GUISet", gui_set, 1040)
        ability = changes.get("ability")
        if ability:
            results["Ability.FunctionEnable"] = camera.set_command(
                "Ability.FunctionEnable", ability, 1040)
        encode_channels = changes.get("encode_channels")
        if encode_channels:
            for chn, entry in encode_channels:
                command = "NetUse.DigitalEncode.[%d]" % chn
                results[command] = camera.set_command(command, entry, 1040)
        encode_smart = changes.get("encode_smart")
        if encode_smart:
            for chn, mode, config in encode_smart:
                if mode == "v2":
                    command = "AVEnc.SmartH264V2.[%d]" % chn
                else:
                    command = "AVEnc.SmartH264.[%d]" % chn
                results[command] = camera.set_command(command, config, 1040)
        av_encode = changes.get("av_encode")
        if av_encode is not None:
            results["Simplify.Encode"] = camera.set_command(
                "Simplify.Encode", av_encode, 1040)
        camera_param = changes.get("camera_param")
        if camera_param:
            for chn, config in camera_param:
                command = "Camera.Param.[%d]" % chn
                results[command] = camera.set_command(command, config, 1040)
        camera_ex_param = changes.get("camera_ex_param")
        if camera_ex_param:
            for chn, config in camera_ex_param:
                command = "Camera.ParamEx.[%d]" % chn
                results[command] = camera.set_command(command, config, 1040)
        white_light = changes.get("white_light")
        if white_light:
            for command, config in white_light:
                results[command] = camera.set_command(command, config, 1040)
        for key, command in (("uart_comm", "Uart.Comm"), ("uart_ptz", "Uart.PTZ"),
                             ("uart_rs485", "Uart.RS485")):
            data = changes.get(key)
            if data:
                results[command] = camera.set_command(command, data, 1040)
        return results


class MjpegDecoder(QObject):
    """Decode a raw H.264/H.265/... elementary stream into JPEG frames.

    The netip media stream is piped through ffmpeg, which autodetects the
    codec, so any codec it supports works.  Complete JPEG frames are
    emitted from the reader thread as raw bytes.
    """

    CODEC_FORMATS = {"h264": "h264", "h265": "hevc", "mpeg4": "m4v", "jpeg": "mjpeg"}
    OUTPUT_SCALE = 1280
    frame_ready = Signal(int, bytes)
    failed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process = None
        self._reader = None
        self._lock = threading.Lock()
        self._stopped = False
        self.generation = 0
        self.codec = None

    @staticmethod
    def available():
        return FFMPEG_BINARY is not None

    def start(self, codec=None):
        self._stopped = False
        self.codec = codec
        command = [FFMPEG_BINARY, "-hide_banner", "-loglevel", "error",
                   "-analyzeduration", "300000", "-flags", "low_delay"]
        input_format = self.CODEC_FORMATS.get(codec or "")
        if input_format:
            command += ["-f", input_format]
        command += ["-i", "pipe:0"]
        if self.OUTPUT_SCALE:
            command += ["-vf", "scale='min(%d,iw)':-2" % self.OUTPUT_SCALE]
        command += ["-f", "mjpeg", "-q:v", "5", "pipe:1"]
        try:
            self._process = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        except OSError as error:
            self._stopped = True
            self.failed.emit("ffmpeg: %s" % error)
            return False
        self._reader = threading.Thread(
            target=self._read_frames, args=(self.generation,), daemon=True)
        self._reader.start()
        return True

    def push_jpeg(self, data):
        self.frame_ready.emit(self.generation, bytes(data))

    def feed(self, data, codec=None):
        if self._stopped:
            return
        if self._process is None and not self.start(codec):
            return
        process = self._process
        if process is None or process.stdin is None:
            return
        try:
            with self._lock:
                process.stdin.write(data)
                process.stdin.flush()
        except (BrokenPipeError, OSError):
            self._stopped = True
            self.failed.emit("ffmpeg pipe closed")

    def _read_frames(self, generation):
        process = self._process
        buffer = bytearray()
        while True:
            try:
                chunk = process.stdout.read(65536)
            except OSError:
                break
            if not chunk:
                break
            buffer.extend(chunk)
            while True:
                start = buffer.find(b"\xff\xd8")
                if start < 0:
                    break
                end = buffer.find(b"\xff\xd9", start + 2)
                if end < 0:
                    if start > 0:
                        del buffer[:start]
                    break
                self.frame_ready.emit(generation, bytes(buffer[start:end + 2]))
                del buffer[:end + 2]
        if not self._stopped:
            message = ""
            if process.stderr is not None:
                try:
                    message = process.stderr.read().decode("utf-8", "replace").strip()
                except OSError:
                    message = ""
            lines = message.splitlines()
            self.failed.emit(lines[-1] if lines else "ffmpeg stream ended")

    def stop(self):
        self._stopped = True
        process = self._process
        self._process = None
        if process is not None:
            try:
                if process.stdin is not None:
                    process.stdin.close()
            except OSError:
                pass
            try:
                process.terminate()
            except OSError:
                pass
            try:
                process.wait(timeout=5)
            except Exception:
                try:
                    process.kill()
                except OSError:
                    pass
        reader = self._reader
        self._reader = None
        if reader is not None and reader.is_alive():
            reader.join(timeout=3)

    def reset(self):
        self._stopped = False
        self._process = None
        self._reader = None
        self.codec = None

    def restart(self):
        self.stop()
        self.generation += 1
        self.reset()


class NetipSessionThread(QThread):
    """Persistent NETIP session that notices when the connection drops.

    Keeps one socket open and sends the protocol keepalive on schedule.  When
    the socket dies (device rebooted, IP changed, cable pulled, WiFi lost) the
    keepalive fails and ``lost`` is emitted so the UI can drop the connected
    state instead of pretending to be connected forever.
    """

    lost = Signal(str)
    ready = Signal(str)

    def __init__(self, address, username, password, cloud_id="", rps=True,
                 port=34567, interval=5.0, no_md5=False, parent=None):
        super().__init__(parent)
        self._address = address
        self._username = username
        self._password = password
        self._no_md5 = bool(no_md5)
        self._cloud_id = cloud_id or ""
        self._rps = bool(rps)
        self._port = int(port or 34567)
        self._interval = max(3.0, float(interval))
        self._stop = False
        self._camera = None

    def stop(self):
        self._stop = True
        camera = self._camera
        if camera is not None:
            try:
                if camera.socket is not None:
                    camera.socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass

    def run(self):
        camera = None
        try:
            address = self._cloud_id or self._address
            camera = DVRIPCam(address, user=self._username,
                              password=self._password, port=self._port)
            if self._no_md5:
                camera.hash_pass = self._password
            if self._cloud_id:
                load_cloud_patch()
                if self._rps:
                    os.environ["RPS"] = "1"
                else:
                    os.environ.pop("RPS", None)
                camera._cloud_device = True
            elif not tcp_reachable(self._address, self._port):
                self.lost.emit("Cannot connect to %s:%s (unreachable)" % (
                    self._address, self._port))
                return
            camera.connect(timeout=8.0)
            if self._stop:
                return
            if not camera.login():
                self.lost.emit(login_failure_text(camera))
                return
            self._camera = camera
            try:
                camera.alive.cancel()
            except Exception:
                pass
            self.ready.emit(self._cloud_id or self._address)
            while not self._stop:
                deadline = time.monotonic() + self._interval
                while not self._stop and time.monotonic() < deadline:
                    time.sleep(0.2)
                if self._stop:
                    break
                try:
                    reply = camera.send(1006, {
                        "Name": "KeepAlive",
                        "SessionID": "0x%08X" % camera.session})
                except Exception as error:
                    if not self._stop:
                        self.lost.emit("Connection lost: %s" % (error,))
                    return
                if self._stop:
                    break
                if (not isinstance(reply, dict)
                        or reply.get("Ret") not in camera.OK_CODES):
                    self.lost.emit("Connection lost (no keepalive reply)")
                    return
        except Exception as error:
            if not self._stop:
                self.lost.emit("%s: %s" % (type(error).__name__, error))
        finally:
            self._camera = None
            if camera is not None:
                try:
                    camera.close()
                except Exception:
                    pass


class NetipVideoThread(QThread):
    status = Signal(str)
    stats = Signal(str)
    failed = Signal(str)
    keyframe = Signal()
    MEDIA_TYPES = {0: "jpeg", 1: "mpeg4", 2: "h264", 3: "h265"}

    def __init__(self, address, username, password, sink, cloud_id="", rps=True,
                 port=34567, stream="Main", channel=0, parent=None,
                 audio_sink=None, no_md5=False):
        super().__init__(parent)
        self._address = address
        self._username = username
        self._password = password
        self._no_md5 = bool(no_md5)
        self._sink = sink
        self._audio_sink = audio_sink
        self._cloud_id = cloud_id or ""
        self._rps = bool(rps)
        self._port = int(port or 34567)
        self._stream = stream
        self._channel = int(channel)
        self._camera = None
        self._stop = False
        self._read_errors = 0
        self._empty_reads = 0
        self._pending = None
        self._pending_lock = threading.Lock()
        self._recv_buf = bytearray()
        self._last_seq = None
        self._packet_seq = None
        self._resync = False
        self._socket_closed = False
        self._need_keyframe = True
        self._win_start = 0.0
        self._win_frames = 0
        self._win_bytes = 0

    def switch(self, stream, channel):
        with self._pending_lock:
            self._pending = (stream, channel)
        self.status.emit("Switching to %s channel %d ..." % (stream, int(channel) + 1))

    def _take_pending(self):
        with self._pending_lock:
            pending = self._pending
            self._pending = None
        return pending

    @staticmethod
    def _params(stream, channel):
        return {
            "Channel": int(channel),
            "CombinMode": "NONE",
            "StreamType": stream,
            "TransMode": "TCP",
        }

    def _switch_stream(self, camera, stream, channel):
        """Stop the old channel and start the new one on a fresh session.

        The device keeps streaming the old channel (and keeps the claim
        locked) if we merely send Start again, so both streams would get
        mixed.  Stop halts it, then a new session gives a fresh keyframe.
        """
        try:
            camera.send(
                1410,
                {
                    "Name": "OPMonitor",
                    "SessionID": "0x%08X" % camera.session,
                    "OPMonitor": {"Action": "Stop",
                                  "Parameter": self._params(self._stream, self._channel)},
                },
                wait_response=False,
            )
        except Exception:
            pass
        try:
            camera.close()
        except Exception:
            pass
        camera = self._open_camera()
        self._camera = camera
        self._claim_and_start(camera, stream, channel)
        self._stream = stream
        self._channel = int(channel)
        self._empty_reads = 0
        self._last_seq = None
        self._resync = False
        self._need_keyframe = True
        self._win_start = 0.0
        self._win_frames = 0
        self._win_bytes = 0
        self._recv_buf.clear()
        self.status.emit("Streaming %s channel %d from %s" % (
            stream, int(channel) + 1, self._cloud_id or self._address))
        return camera

    def stop(self):
        self._stop = True

    def _open_camera(self):
        address = self._cloud_id or self._address
        camera = DVRIPCam(address, user=self._username,
                          password=self._password, port=self._port)
        if self._no_md5:
            camera.hash_pass = self._password
        if self._cloud_id:
            load_cloud_patch()
            if self._rps:
                os.environ["RPS"] = "1"
            else:
                os.environ.pop("RPS", None)
            camera._cloud_device = True
        elif not tcp_reachable(self._address, self._port):
            raise RuntimeError("Cannot connect to %s:%s (unreachable)" % (
                self._address, self._port))
        camera.connect(timeout=8.0)
        if not camera.login():
            raise RuntimeError(login_failure_text(camera))
        camera.timeout = 5
        return camera

    def _claim_and_start(self, camera, stream, channel):
        params = self._params(stream, channel)
        reply = camera.set_command(
            "OPMonitor", {"Action": "Claim", "Parameter": params})
        ret = reply.get("Ret") if isinstance(reply, dict) else reply
        if ret not in camera.OK_CODES:
            raise RuntimeError("OPMonitor claim failed: Ret=%s (%s)" % (
                ret, RESULT_CODES.get(ret, "unknown")))
        camera.send(
            1410,
            {
                "Name": "OPMonitor",
                "SessionID": "0x%08X" % camera.session,
                "OPMonitor": {"Action": "Start", "Parameter": params},
            },
            wait_response=False,
        )
        try:
            camera.socket.settimeout(0.25)
        except (AttributeError, OSError):
            pass

    def run(self):
        if DVRIPCam is None:
            self.failed.emit("python-dvr (dvrip.py) is not available")
            return
        camera = None
        try:
            camera = self._open_camera()
            self._camera = camera
            self._claim_and_start(camera, self._stream, self._channel)
            self._last_seq = None
            self._resync = False
            self._need_keyframe = True
            self._win_start = 0.0
            self._win_frames = 0
            self._win_bytes = 0
            self._recv_buf.clear()
            self.status.emit("Streaming %s channel %d from %s" % (
                self._stream, self._channel + 1, self._cloud_id or self._address))
            camera = self._stream_loop(camera)
        except Exception as error:
            if not self._stop:
                self.failed.emit("%s: %s" % (type(error).__name__, error))
        finally:
            self._camera = None
            if camera is not None:
                try:
                    camera.stop_monitor()
                except Exception:
                    pass
                try:
                    camera.close()
                except Exception:
                    pass

    def _recv_exact(self, camera, length, idle_timeout, allow_pending=False):
        buf = bytearray()
        idle = time.monotonic()
        while len(buf) < length:
            if self._stop:
                return None
            if allow_pending and not buf and not self._recv_buf and self._pending is not None:
                return None
            if self._recv_buf:
                need = length - len(buf)
                buf.extend(self._recv_buf[:need])
                del self._recv_buf[:need]
                idle = time.monotonic()
                continue
            try:
                chunk = camera.socket.recv(65536)
            except socket.timeout:
                if time.monotonic() - idle > idle_timeout:
                    return None
                continue
            except OSError:
                if not self._stop:
                    self._socket_closed = True
                return None
            if not chunk:
                if not self._stop:
                    self._socket_closed = True
                return None
            self._recv_buf.extend(chunk)
        return bytes(buf)

    @staticmethod
    def _is_jpeg_frame(frame):
        return bool(frame) and bytes(frame[:2]) == b"\xff\xd8"

    @staticmethod
    def _is_frame_start(payload):
        if len(payload) < 4:
            return False
        data_type = struct.unpack(">I", payload[:4])[0]
        return data_type in (0x1FC, 0x1FE, 0x1FD, 0x1FA, 0x1F9) or data_type == 0xFFD8FFE0

    def _read_packet(self, camera):
        """Read one media packet (20-byte header + payload), boundary safe."""
        if self._pending is not None or self._stop:
            return None
        header = self._recv_exact(camera, 20, 0.5, allow_pending=True)
        if header is None:
            return None
        try:
            head, version, _session, seq, _total, _cur, msgid, payload_len = struct.unpack(
                "BB2xIIBBHI", header)
        except struct.error:
            self._resync = True
            return None
        if head != 0xFF or version != 1 or msgid != 1412 or payload_len > (4 << 20):
            self._resync = True
            return None
        payload = self._recv_exact(camera, payload_len, 1.5)
        if payload is None:
            self._resync = True
            return None
        if (self._last_seq is not None
                and seq != ((self._last_seq + 1) & 0xFFFFFFFF)
                and not self._is_frame_start(payload)):
            self._resync = True
            return None
        self._last_seq = seq
        self._packet_seq = seq
        return payload

    def _resync_packet(self, camera):
        """Scan the byte stream for the next valid media packet header."""
        idle = time.monotonic()
        while not self._stop:
            if self._pending is not None:
                return None
            index = self._recv_buf.find(b"\xff\x01")
            if index >= 0 and len(self._recv_buf) >= index + 20:
                candidate = bytes(self._recv_buf[index:index + 20])
                try:
                    _head, _version, _session, seq, _total, _cur, msgid, payload_len = struct.unpack(
                        "BB2xIIBBHI", candidate)
                except struct.error:
                    del self._recv_buf[:index + 1]
                    continue
                if msgid == 1412 and payload_len <= (4 << 20):
                    del self._recv_buf[:index + 20]
                    payload = self._recv_exact(camera, payload_len, 1.5)
                    if payload is None:
                        return None
                    if (self._last_seq is None
                            or seq == ((self._last_seq + 1) & 0xFFFFFFFF)
                            or self._is_frame_start(payload)):
                        self._last_seq = seq
                        self._packet_seq = seq
                        return payload
                    continue
                del self._recv_buf[:index + 1]
                continue
            if index >= 0:
                del self._recv_buf[:index]
            try:
                chunk = camera.socket.recv(65536)
            except socket.timeout:
                if time.monotonic() - idle > 1.5:
                    return None
                continue
            except OSError:
                return None
            if not chunk:
                return None
            idle = time.monotonic()
            self._recv_buf.extend(chunk)
        return None

    def _read_media(self, camera):
        """Read one media message, tolerating bad timestamps and resyncing."""
        if self._resync:
            packet = self._resync_packet(camera)
            if packet is None:
                return None, {}
            self._resync = False
        else:
            packet = self._read_packet(camera)
            if packet is None:
                return None, {}
        meta = {"seq": self._packet_seq}
        length = 0
        buf = bytearray()
        while True:
            frame_len = 0
            if length == 0:
                if len(packet) < 8:
                    self._resync = True
                    return None, meta
                data_type = struct.unpack(">I", packet[:4])[0]
                if data_type in (0x1FC, 0x1FE):
                    if len(packet) < 16:
                        self._resync = True
                        return None, meta
                    media, fps, width, height, _dt, length = struct.unpack(
                        "BBBBII", packet[4:16])
                    meta["fps"] = fps
                    meta["width"] = width * 8
                    meta["height"] = height * 8
                    meta["frame"] = "I" if data_type == 0x1FC else "P"
                    meta["type"] = NetipVideoThread.MEDIA_TYPES.get(media & 0x0F)
                    frame_len = 16
                elif data_type == 0x1FD:
                    (length,) = struct.unpack("I", packet[4:8])
                    meta["frame"] = "P"
                    frame_len = 8
                elif data_type == 0x1FA:
                    media, _rate, length = struct.unpack("BBH", packet[4:8])
                    meta["type"] = "g711a" if media == 0xE else "audio"
                    frame_len = 8
                elif data_type == 0x1F9:
                    _media, _count, length = struct.unpack("BBH", packet[4:8])
                    meta["type"] = "info"
                    frame_len = 8
                elif data_type == 0xFFD8FFE0:
                    return packet, meta
                else:
                    self._resync = True
                    return None, meta
            buf.extend(packet[frame_len:])
            length -= len(packet) - frame_len
            if length <= 0:
                return bytes(buf), meta
            packet = self._read_packet(camera)
            if packet is None:
                if not self._stop and self._pending is None:
                    self._resync = True
                return None, meta

    def _stream_loop(self, camera):
        while not self._stop:
            pending = self._take_pending()
            if pending is not None:
                try:
                    camera = self._switch_stream(camera, pending[0], pending[1])
                except Exception as error:
                    if not self._stop:
                        self.failed.emit("Switch failed: %s: %s" % (
                            type(error).__name__, error))
                    break
            try:
                frame, meta = self._read_media(camera)
            except Exception as error:
                if self._stop:
                    break
                self._read_errors += 1
                if self._read_errors == 1:
                    self.status.emit("Stream read error: %s: %s" % (
                        type(error).__name__, error))
                continue
            if self._stop:
                break
            if not frame:
                if self._socket_closed and not self._stop:
                    self.failed.emit("Connection lost — stream stopped")
                    break
                self._empty_reads += 1
                if self._empty_reads == 3:
                    self.status.emit("No media data received (channel offline?)")
                continue
            self._empty_reads = 0
            codec = meta.get("type") if isinstance(meta, dict) else None
            if codec in ("g711a", "audio", "info"):
                if (codec in ("g711a", "audio")
                        and self._audio_sink is not None):
                    self._audio_sink.feed_audio(frame)
                continue
            if self._need_keyframe:
                if not codec:
                    continue
                if (meta.get("frame") != "I" and codec != "jpeg"
                        and not self._is_jpeg_frame(frame)):
                    continue
                self._need_keyframe = False
                self._sink.restart()
                self._win_start = 0.0
                self._win_frames = 0
                self._win_bytes = 0
                self.keyframe.emit()
            elif codec and self._sink.codec != codec:
                self._sink.restart()
            data = bytes(frame)
            keyframe = bool(isinstance(meta, dict)
                            and meta.get("frame") == "I")
            if data[:2] == b"\xff\xd8":
                self._sink.push_jpeg(data, keyframe)
            else:
                self._sink.feed(data, codec, keyframe)
            now = time.monotonic()
            if self._win_start == 0.0:
                self._win_start = now
            self._win_frames += 1
            self._win_bytes += len(data)
            elapsed = now - self._win_start
            if elapsed >= 1.0:
                self.stats.emit("%.1f fps  %.0f kbps" % (
                    self._win_frames / elapsed,
                    self._win_bytes * 8.0 / elapsed / 1000.0))
                self._win_start = now
                self._win_frames = 0
                self._win_bytes = 0
        if not self._stop:
            self.failed.emit("Stream ended")
        return camera


def version_key(value):
    parts = [int(part) for part in re.findall(r"\d+", str(value or ""))[:4]]
    while len(parts) < 4:
        parts.append(0)
    return tuple(parts)


def format_date(value):
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        return datetime.fromisoformat(
            text.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError:
        return text


def remote_is_newer(remote, local):
    """Compare a GitHub timestamp with the local commit/build timestamp."""
    remote = str(remote or "").strip()
    local = str(local or "").strip()
    if not remote or not local:
        return False
    if len(local) > 10:
        try:
            remote_dt = datetime.fromisoformat(remote.replace("Z", "+00:00"))
            local_dt = datetime.fromisoformat(local.replace("Z", "+00:00"))
            return remote_dt > local_dt
        except ValueError:
            pass
    return format_date(remote) > format_date(local)


class ReleaseCheckThread(QThread):
    """Fetch the latest GitHub release, or the latest commit as a fallback."""

    result = Signal(dict)
    error = Signal(str)
    API = "https://api.github.com/repos/%s" % GITHUB_REPO
    HEADERS = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "XMDMS/%s" % APP_VERSION,
        "X-GitHub-Api-Version": "2022-11-28",
    }

    def _get(self, path):
        request = urllib.request.Request(self.API + path, headers=self.HEADERS)
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def _latest_commit(self):
        last_error = None
        for branch in ("main", "master"):
            try:
                data = self._get("/commits/%s" % branch)
                commit = data.get("commit") if isinstance(data, dict) else {}
                message = commit.get("message") if isinstance(commit, dict) else ""
                author = commit.get("author") if isinstance(commit, dict) else {}
                return {
                    "kind": "commit",
                    "branch": branch,
                    "sha": str(data.get("sha") or ""),
                    "message": str(message or ""),
                    "date": str(author.get("date") or ""),
                    "url": str(data.get("html_url") or ""),
                }
            except urllib.error.HTTPError as error:
                last_error = error
                if error.code != 404:
                    raise
        if last_error is not None:
            raise last_error
        raise RuntimeError("No repository commits found")

    def run(self):
        try:
            try:
                data = self._get("/releases/latest")
            except urllib.error.HTTPError as error:
                if error.code != 404:
                    raise
                data = None
            if isinstance(data, dict) and data.get("tag_name"):
                self.result.emit({
                    "kind": "release",
                    "tag": str(data.get("tag_name") or ""),
                    "name": str(data.get("name") or ""),
                    "body": str(data.get("body") or ""),
                    "date": str(data.get("published_at") or ""),
                    "url": str(data.get("html_url") or ""),
                })
                return
            self.result.emit(self._latest_commit())
        except urllib.error.HTTPError as error:
            if error.code in (403, 429):
                self.error.emit("GitHub API rate limit reached")
            elif error.code == 404:
                self.error.emit("No releases or commits found")
            else:
                self.error.emit("GitHub API error: HTTP %s" % error.code)
        except urllib.error.URLError as error:
            self.error.emit("Network error: %s" % (error.reason or error))
        except Exception as error:
            self.error.emit("%s: %s" % (type(error).__name__, error))


class DeviceTableModel(QAbstractTableModel):
    SORT_ROLE = Qt.ItemDataRole.UserRole + 1
    check_state_changed = Signal(object)
    COLUMNS = (
        ("", "check"),
        ("#", None),
        ("IP", "ip"),
        ("MAC", "mac"),
        ("SN", "sn"),
        ("Version", "version"),
        ("Build Date", "build_date"),
        ("Host Name", "host_name"),
    )

    @staticmethod
    def identity(device):
        return device.get("cloud_id") or device.get("sn") or device.get("ip")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._devices = []
        self._rows = {}
        self._checked = set()
        self._connected = set()
        self._provision = {}
        self._sort_column = 2
        self._sort_order = Qt.SortOrder.AscendingOrder

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._devices)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.COLUMNS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return tr(self.COLUMNS[section][0])
        return None

    def flags(self, index):
        base = super().flags(index)
        if index.isValid() and self.COLUMNS[index.column()][1] == "check":
            return base | Qt.ItemFlag.ItemIsUserCheckable
        return base

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.CheckStateRole and self.COLUMNS[index.column()][1] == "check":
            identity = self.identity(self._devices[index.row()])
            if Qt.CheckState(value) == Qt.CheckState.Checked:
                self._checked.add(identity)
            else:
                self._checked.discard(identity)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
            self.check_state_changed.emit(self.checked_state())
            return True
        return False

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        device = self._devices[index.row()]
        if role == Qt.ItemDataRole.BackgroundRole:
            identity = self.identity(device)
            state = self._provision.get(identity)
            if state == "failed":
                return PROVISION_FAILED_BRUSH
            if state == "ok":
                return PROVISION_OK_BRUSH
            if state == "active":
                return PROVISION_ACTIVE_BRUSH
            return CONNECTED_BRUSH if identity in self._connected else None
        key = self.COLUMNS[index.column()][1]
        if key == "check":
            if role == Qt.ItemDataRole.CheckStateRole:
                identity = self.identity(device)
                return Qt.CheckState.Checked if identity in self._checked else Qt.CheckState.Unchecked
            return None
        if key is None:
            if role in (Qt.ItemDataRole.DisplayRole, self.SORT_ROLE):
                return index.row() + 1
            return None
        value = device.get(key)
        if key == "sn" and not value:
            value = device.get("cloud_id")
        if key == "sn" and not value:
            raw = device.get("raw") or {}
            value = raw.get("SerialNo") or raw.get("SN")
        if role == Qt.ItemDataRole.DisplayRole:
            if value is None:
                return ""
            if key == "version":
                return str(value)[:18]
            return str(value)
        if role == self.SORT_ROLE:
            return self._sort_key(key, value)
        return None

    def _sort_key(self, key, value):
        if key in ("ip", "gateway", "subnet"):
            return ip_sort_key(value or "")
        if key.endswith("_port"):
            try:
                return int(value)
            except (TypeError, ValueError):
                return -1
        return ("" if value is None else str(value)).lower()

    def _active_sort_key(self):
        key = self.COLUMNS[self._sort_column][1]
        return key if key and key != "check" else "ip"

    def sort(self, column, order=Qt.SortOrder.AscendingOrder):
        if column < 0 or column >= len(self.COLUMNS):
            return
        self._sort_column = column
        self._sort_order = order
        self._resort()

    def _resort(self):
        key = self._active_sort_key()
        self.layoutAboutToBeChanged.emit()
        self._devices.sort(
            key=lambda device: self._sort_key(key, device.get(key)),
            reverse=self._sort_order == Qt.SortOrder.DescendingOrder,
        )
        self._rows = {
            self.identity(device): row
            for row, device in enumerate(self._devices)
        }
        self.layoutChanged.emit()

    def upsert(self, device):
        identity = self.identity(device)
        row = self._rows.get(identity)
        if row is None:
            self._devices.append(device)
            self._resort()
            self.check_state_changed.emit(self.checked_state())
            return True
        previous = self._devices[row]
        key = self._active_sort_key()
        old_key = self._sort_key(key, previous.get(key))
        previous.update(device)
        new_key = self._sort_key(key, previous.get(key))
        if new_key != old_key:
            self._resort()
        else:
            self.dataChanged.emit(
                self.index(row, 0), self.index(row, len(self.COLUMNS) - 1))
        return False

    def checked_devices(self):
        return [device for device in self._devices if self.identity(device) in self._checked]

    def devices(self):
        return list(self._devices)

    def device_at(self, row):
        if 0 <= row < len(self._devices):
            return self._devices[row]
        return None

    def checked_state(self):
        total = len(self._devices)
        if total == 0:
            return Qt.CheckState.Unchecked
        checked = sum(1 for device in self._devices if self.identity(device) in self._checked)
        if checked == 0:
            return Qt.CheckState.Unchecked
        if checked == total:
            return Qt.CheckState.Checked
        return Qt.CheckState.PartiallyChecked

    def set_all_checked(self, checked):
        if checked:
            self._checked = {self.identity(device) for device in self._devices}
        else:
            self._checked.clear()
        if self._devices:
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(len(self._devices) - 1, 0),
                [Qt.ItemDataRole.CheckStateRole])
        self.check_state_changed.emit(self.checked_state())

    def remove_device(self, row):
        if not 0 <= row < len(self._devices):
            return
        device = self._devices[row]
        self.beginRemoveRows(QModelIndex(), row, row)
        self._devices.pop(row)
        self._checked.discard(self.identity(device))
        self._connected.discard(self.identity(device))
        self._provision.pop(self.identity(device), None)
        self._rows = {
            self.identity(item): index
            for index, item in enumerate(self._devices)
        }
        self.endRemoveRows()
        self.check_state_changed.emit(self.checked_state())

    def clear(self):
        self.beginResetModel()
        self._devices = []
        self._rows = {}
        self._checked = set()
        self._connected = set()
        self._provision = {}
        self.endResetModel()
        self.check_state_changed.emit(self.checked_state())

    def set_connected(self, identity, connected):
        if connected:
            self._connected.add(identity)
        else:
            self._connected.discard(identity)
        row = self._rows.get(identity)
        if row is not None:
            self.dataChanged.emit(
                self.index(row, 0), self.index(row, len(self.COLUMNS) - 1))

    def is_connected(self, identity):
        return identity in self._connected

    def set_device_ip(self, device, address):
        old_identity = self.identity(device)
        device["ip"] = address
        raw = device.get("raw")
        if isinstance(raw, dict) and "HostIP" in raw:
            raw["HostIP"] = address
        new_identity = self.identity(device)
        if new_identity != old_identity:
            row = self._rows.pop(old_identity, None)
            for store in (self._checked, self._connected):
                if old_identity in store:
                    store.discard(old_identity)
                    store.add(new_identity)
            if old_identity in self._provision:
                self._provision[new_identity] = self._provision.pop(old_identity)
            if row is not None:
                self._rows[new_identity] = row
        self._resort()
        return new_identity

    def set_provision_state(self, identity, state):
        if state:
            self._provision[identity] = state
        else:
            self._provision.pop(identity, None)
        row = self._rows.get(identity)
        if row is not None:
            self.dataChanged.emit(
                self.index(row, 0), self.index(row, len(self.COLUMNS) - 1))

    def clear_provision_states(self):
        if not self._provision:
            return
        self._provision = {}
        if self._devices:
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(len(self._devices) - 1, len(self.COLUMNS) - 1))


class IpAddressEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._octets = []
        for index in range(4):
            if index:
                layout.addWidget(QLabel("."))
            octet = QLineEdit()
            octet.setMaxLength(3)
            octet.setFixedWidth(46)
            octet.setAlignment(Qt.AlignmentFlag.AlignCenter)
            octet.setValidator(QIntValidator(0, 255, octet))
            octet.installEventFilter(self)
            octet.textChanged.connect(lambda text, position=index: self._on_text_changed(position, text))
            layout.addWidget(octet)
            self._octets.append(octet)
        layout.addStretch(1)

    def eventFilter(self, watched, event):
        if isinstance(watched, QLineEdit) and event.type() == QEvent.Type.KeyPress:
            index = self._octets.index(watched)
            if event.key() == Qt.Key.Key_Period:
                if index < 3:
                    self._focus_octet(index + 1)
                return True
            if event.key() == Qt.Key.Key_Backspace and not watched.text() and watched.cursorPosition() == 0 and index > 0:
                previous = self._octets[index - 1]
                self._focus_octet(index - 1)
                previous.backspace()
                return True
            if event.key() == Qt.Key.Key_Left and watched.cursorPosition() == 0 and index > 0:
                previous = self._octets[index - 1]
                previous.setFocus()
                previous.setCursorPosition(len(previous.text()))
                return True
            if event.key() == Qt.Key.Key_Right and watched.cursorPosition() == len(watched.text()) and index < 3:
                self._focus_octet(index + 1)
                return True
        return super().eventFilter(watched, event)

    def _focus_octet(self, index):
        octet = self._octets[index]
        octet.setFocus()
        octet.selectAll()

    def _on_text_changed(self, index, text):
        if index >= 3 or not text.isdigit():
            return
        if len(text) == 3 or (len(text) == 2 and int(text) > 25):
            self._focus_octet(index + 1)

    def value(self):
        parts = []
        for octet in self._octets:
            text = octet.text()
            if not text.isdigit():
                return ""
            number = int(text)
            if number > 255:
                return ""
            parts.append(str(number))
        return ".".join(parts)

    def setValue(self, text):
        parts = str(text or "").split(".")
        for index, octet in enumerate(self._octets):
            value = parts[index] if index < len(parts) else ""
            octet.blockSignals(True)
            octet.setText(value if value.isdigit() else "")
            octet.blockSignals(False)


class CheckableHeaderView(QHeaderView):
    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self._state = Qt.CheckState.Unchecked

    def set_check_state(self, state):
        self._state = Qt.CheckState(state)
        self.viewport().update()

    def paintSection(self, painter, rect, logicalIndex):
        super().paintSection(painter, rect, logicalIndex)
        if logicalIndex != 0:
            return
        option = QStyleOptionButton()
        option.state = QStyle.StateFlag.State_Enabled
        if self._state == Qt.CheckState.Checked:
            option.state |= QStyle.StateFlag.State_On
        elif self._state == Qt.CheckState.PartiallyChecked:
            option.state |= QStyle.StateFlag.State_NoChange
        else:
            option.state |= QStyle.StateFlag.State_Off
        size = self.style().pixelMetric(QStyle.PixelMetric.PM_IndicatorWidth)
        option.rect = QRect(
            rect.x() + (rect.width() - size) // 2,
            rect.y() + (rect.height() - size) // 2,
            size, size)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorCheckBox, option, painter)

    def mousePressEvent(self, event):
        if self.logicalIndexAt(event.position().toPoint()) == 0:
            self.toggled.emit(self._state != Qt.CheckState.Checked)
            return
        super().mousePressEvent(event)


class AddDeviceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add device")
        self.address_edit = IpAddressEdit()
        self.address_edit.setValue("192.168.1.10")
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(34567)
        self.port_spin.setMaximumWidth(80)
        self.no_md5_check = QCheckBox("NOMD5")
        self.no_md5_check.setToolTip(
            "Send the password as-is instead of the MD5/sofia hash.")
        self.user_edit = QLineEdit("admin")
        self.password_edit = QLineEdit()
        configure_password_edit(self.password_edit)
        self.cloud_edit = QLineEdit()
        self.cloud_edit.setPlaceholderText("SN, overrides IP")
        self.cloud_edit.textChanged.connect(self._cloud_changed)
        self.rps_check = QCheckBox("RPS")
        self.rps_check.setChecked(True)
        if not cloud_patch_available():
            note = "xmcloud.py not available — cloud/SN transport disabled"
            self.cloud_edit.setEnabled(False)
            self.rps_check.setEnabled(False)
            self.cloud_edit.setToolTip(note)
            self.rps_check.setToolTip(note)

        form = QGridLayout()
        form.addWidget(QLabel("IP address:"), 0, 0)
        form.addWidget(self.address_edit, 0, 1)
        port_row = QHBoxLayout()
        port_row.setContentsMargins(0, 0, 0, 0)
        port_row.addWidget(self.port_spin)
        port_row.addWidget(self.no_md5_check)
        port_row.addStretch(1)
        form.addWidget(QLabel("Port:"), 1, 0)
        form.addLayout(port_row, 1, 1)
        form.addWidget(QLabel("Login:"), 2, 0)
        form.addWidget(self.user_edit, 2, 1)
        form.addWidget(QLabel("Password:"), 3, 0)
        form.addWidget(self.password_edit, 3, 1)
        form.addWidget(QLabel("CloudID:"), 4, 0)
        form.addWidget(self.cloud_edit, 4, 1)
        form.addWidget(QLabel("Transport:"), 5, 0)
        form.addWidget(self.rps_check, 5, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _cloud_changed(self, text):
        if not self.cloud_edit.isEnabled():
            self.address_edit.setEnabled(True)
            return
        self.address_edit.setEnabled(not text.strip())

    def set_user(self, user):
        self.user_edit.setText(user or "admin")

    def set_password(self, password):
        self.password_edit.setText(password or "")

    def set_values(self, device):
        self.address_edit.setValue(device.get("ip") or "")
        self.port_spin.setValue(int(device.get("tcp_port") or 34567))
        self.no_md5_check.setChecked(bool(device.get("no_md5")))
        self.user_edit.setText(device.get("username") or "admin")
        self.password_edit.setText(device.get("password") or "")
        self.cloud_edit.setText(device.get("cloud_id") or "")
        self.rps_check.setChecked(bool(device.get("rps", True)))
        self._cloud_changed(self.cloud_edit.text())

    def address(self):
        return self.address_edit.value()

    def port(self):
        return int(self.port_spin.value())

    def username(self):
        return self.user_edit.text().strip() or "admin"

    def password(self):
        return self.password_edit.text()

    def cloud_id(self):
        return self.cloud_edit.text().strip()

    def rps(self):
        return self.rps_check.isChecked()

    def no_md5(self):
        return self.no_md5_check.isChecked()


class AuthorityListWidget(QListWidget):
    def __init__(self, authorities=(), checked=(), parent=None):
        super().__init__(parent)
        checked = set(checked)
        for name in authorities:
            item = QListWidgetItem(str(name))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if name in checked else Qt.CheckState.Unchecked)
            self.addItem(item)

    def checked_items(self):
        return [self.item(index).text() for index in range(self.count())
                if self.item(index).checkState() == Qt.CheckState.Checked]


class UserDialog(QDialog):
    def __init__(self, parent=None, groups=(), authorities=(), user=None):
        super().__init__(parent)
        self.setWindowTitle("Modify user" if user else "Add user")
        self._adding = user is None
        self.name_edit = QLineEdit()
        self.sharable_check = QCheckBox("Reuseable")
        self.password_edit = QLineEdit()
        configure_password_edit(self.password_edit)
        self.confirm_edit = QLineEdit()
        configure_password_edit(self.confirm_edit)
        self.group_combo = QComboBox()
        self._group_authorities = {}
        for group in groups:
            if isinstance(group, dict):
                name = str(group.get("Name") or "")
                rights = group.get("AuthorityList")
            else:
                name = str(group)
                rights = []
            self._group_authorities[name] = rights if isinstance(rights, list) else []
            self.group_combo.addItem(name, name)
        self.memo_edit = QLineEdit()
        self.memo_edit.setMaxLength(31)
        if isinstance(user, dict):
            checked = user.get("AuthorityList") or ()
        elif self.group_combo.count():
            checked = self._group_authorities.get(self.group_combo.currentText(), ())
        else:
            checked = ()
        self.authority_list = AuthorityListWidget(authorities, checked)
        self.group_combo.currentTextChanged.connect(self._group_changed)
        form = QGridLayout()
        form.addWidget(QLabel("User:"), 0, 0)
        form.addWidget(self.name_edit, 0, 1)
        form.addWidget(self.sharable_check, 0, 2)
        if user is None:
            form.addWidget(QLabel("Password:"), 1, 0)
            form.addWidget(self.password_edit, 1, 1)
            form.addWidget(QLabel("Confirm:"), 2, 0)
            form.addWidget(self.confirm_edit, 2, 1)
        form.addWidget(QLabel("Group:"), 3, 0)
        form.addWidget(self.group_combo, 3, 1)
        form.addWidget(QLabel("Memo:"), 4, 0)
        form.addWidget(self.memo_edit, 4, 1)
        all_button = QPushButton("All")
        none_button = QPushButton("None")
        all_button.clicked.connect(lambda: self._set_all(Qt.CheckState.Checked))
        none_button.clicked.connect(lambda: self._set_all(Qt.CheckState.Unchecked))
        authority_buttons = QHBoxLayout()
        authority_buttons.addWidget(QLabel("Authority:"))
        authority_buttons.addStretch(1)
        authority_buttons.addWidget(all_button)
        authority_buttons.addWidget(none_button)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(authority_buttons)
        layout.addWidget(self.authority_list, 1)
        layout.addWidget(buttons)
        self.resize(360, 480)
        if user is not None:
            self.name_edit.setText(str(user.get("Name") or ""))
            self.sharable_check.setChecked(bool(user.get("Sharable")))
            index = self.group_combo.findText(str(user.get("Group") or ""))
            if index >= 0:
                self.group_combo.setCurrentIndex(index)
            self.memo_edit.setText(str(user.get("Memo") or ""))

    def _set_all(self, state):
        for index in range(self.authority_list.count()):
            self.authority_list.item(index).setCheckState(state)

    def _group_changed(self, name):
        if not self._adding:
            return
        checked = set(self._group_authorities.get(name, ()))
        for index in range(self.authority_list.count()):
            item = self.authority_list.item(index)
            item.setCheckState(
                Qt.CheckState.Checked if item.text() in checked
                else Qt.CheckState.Unchecked)

    def values(self):
        return {
            "name": self.name_edit.text().strip(),
            "group": self.group_combo.currentText(),
            "password": self.password_edit.text(),
            "confirm": self.confirm_edit.text(),
            "memo": self.memo_edit.text().strip(),
            "sharable": self.sharable_check.isChecked(),
            "authority": self.authority_list.checked_items(),
        }


class GroupDialog(QDialog):
    def __init__(self, parent=None, authorities=(), group=None):
        super().__init__(parent)
        self.setWindowTitle("Modify group" if group else "Add group")
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(16)
        self.memo_edit = QLineEdit()
        self.memo_edit.setMaxLength(31)
        checked = group.get("AuthorityList") if isinstance(group, dict) else ()
        self.authority_list = AuthorityListWidget(authorities, checked or ())
        form = QGridLayout()
        form.addWidget(QLabel("Group:"), 0, 0)
        form.addWidget(self.name_edit, 0, 1)
        form.addWidget(QLabel("Memo:"), 1, 0)
        form.addWidget(self.memo_edit, 1, 1)
        all_button = QPushButton("All")
        none_button = QPushButton("None")
        all_button.clicked.connect(lambda: self._set_all(Qt.CheckState.Checked))
        none_button.clicked.connect(lambda: self._set_all(Qt.CheckState.Unchecked))
        authority_buttons = QHBoxLayout()
        authority_buttons.addWidget(QLabel("Authority:"))
        authority_buttons.addStretch(1)
        authority_buttons.addWidget(all_button)
        authority_buttons.addWidget(none_button)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(authority_buttons)
        layout.addWidget(self.authority_list, 1)
        layout.addWidget(buttons)
        self.resize(360, 480)
        if group is not None:
            self.name_edit.setText(str(group.get("Name") or ""))
            self.memo_edit.setText(str(group.get("Memo") or ""))

    def _set_all(self, state):
        for index in range(self.authority_list.count()):
            self.authority_list.item(index).setCheckState(state)

    def values(self):
        return {
            "name": self.name_edit.text().strip(),
            "memo": self.memo_edit.text().strip(),
            "authority": self.authority_list.checked_items(),
        }


class PasswordDialog(QDialog):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change password — %s" % name)
        self.old_edit = QLineEdit()
        configure_password_edit(self.old_edit)
        self.new_edit = QLineEdit()
        configure_password_edit(self.new_edit)
        form = QGridLayout()
        form.addWidget(QLabel("Old password:"), 0, 0)
        form.addWidget(self.old_edit, 0, 1)
        form.addWidget(QLabel("New password:"), 1, 0)
        form.addWidget(self.new_edit, 1, 1)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self):
        return self.old_edit.text(), self.new_edit.text()


class EncodeTableDialog(QDialog):
    COLUMNS = ("M res", "M FPS", "M RC", "M quality", "M I-frame",
               "S res", "S FPS", "S RC", "S quality", "S I-frame",
               "Smart M", "Smart S")
    KEYS = ("m_res", "m_fps", "m_rc", "m_quality", "m_gop",
            "s_res", "s_fps", "s_rc", "s_quality", "s_gop",
            "m_smart", "s_smart")

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Encode — all channels")
        self._window = window
        self._rows = {}
        self.resize(1060, 560)

        table = QTableWidget(0, len(self.COLUMNS))
        table.setHorizontalHeaderLabels(self.COLUMNS)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(True)
        table.setSortingEnabled(False)
        self.table = table
        install_copy_menu(table)

        channels = len(window._encode_configs)
        table.setRowCount(channels)
        for chn in range(channels):
            entry = window._encode_entry(chn)
            smart_state = window._encode_smart_state(chn)
            main_names, sub_names = window._encode_resolution_choices(chn)
            fields = {}
            for prefix, names in (("m", main_names), ("s", sub_names)):
                resolution = QComboBox()
                resolution.addItems(names or list(ENCODE_RESOLUTIONS))
                fields[prefix + "_res"] = resolution
                fps = QSpinBox()
                fps.setRange(1, 30)
                fields[prefix + "_fps"] = fps
                rate = QComboBox()
                rate.addItems(ENCODE_RATE_CONTROL)
                fields[prefix + "_rc"] = rate
                quality = QSpinBox()
                quality.setRange(1, 6)
                fields[prefix + "_quality"] = quality
                gop = QSpinBox()
                gop.setRange(1, 250)
                fields[prefix + "_gop"] = gop
            mode = smart_state.get("mode") if isinstance(smart_state, dict) else None
            for key in ("m_smart", "s_smart"):
                smart = QComboBox()
                if mode == "v2":
                    smart.addItems(["Off", "H265+", "H265AI"])
                elif mode == "v1":
                    smart.addItems(["Off", "H265+"])
                else:
                    smart.addItem("Off")
                fields[key] = smart
            for column, key in enumerate(self.KEYS):
                table.setCellWidget(chn, column, fields[key])
            self._rows[chn] = fields
            enabled = isinstance(entry, dict)
            if enabled:
                for prefix, format_key in (("m", "MainFormat"), ("s", "ExtraFormat")):
                    fmt = entry.get(format_key) if isinstance(
                        entry.get(format_key), dict) else {}
                    video = fmt.get("Video") if isinstance(fmt.get("Video"), dict) else {}
                    fields[prefix + "_res"].setCurrentText(
                        str(video.get("Resolution") or ""))
                    for key, source in (("fps", "FPS"), ("quality", "Quality"),
                                        ("gop", "GOP")):
                        try:
                            value = int(video.get(source))
                        except (TypeError, ValueError):
                            value = 1
                        fields[prefix + "_" + key].setValue(value)
                    fields[prefix + "_rc"].setCurrentText(
                        str(video.get("BitRateControl") or "VBR"))
                if isinstance(smart_state, dict):
                    config = smart_state.get("config") or {}
                    for index, key in ((0, "m_smart"), (1, "s_smart")):
                        value = "Off"
                        if mode == "v2":
                            plus = config.get("Smart264PlusV2")
                            v2 = config.get("Smart264V2")
                            plus_on = (isinstance(plus, list) and index < len(plus)
                                       and isinstance(plus[index], dict)
                                       and plus[index].get("SmartH264Plus") == 1)
                            v2_on = (isinstance(v2, list) and index < len(v2)
                                     and isinstance(v2[index], dict)
                                     and v2[index].get("SmartH264"))
                            value = "H265AI" if plus_on else "H265+" if v2_on else "Off"
                        elif config.get("SmartH264"):
                            value = "H265+"
                        fields[key].setCurrentText(value)
            for widget in fields.values():
                widget.setEnabled(enabled)

        footer = QTableWidget(2, len(self.KEYS))
        footer.horizontalHeader().setVisible(False)
        footer.verticalHeader().setVisible(True)
        for row in range(2):
            footer.setVerticalHeaderItem(row, QTableWidgetItem(""))
        footer.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        footer.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        footer.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        footer.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        footer.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        footer.verticalHeader().setDefaultSectionSize(30)
        self.footer = footer
        self._all = {}
        for column, key in enumerate(self.KEYS):
            if key.endswith("_res"):
                editor = QComboBox()
                editor.setEditable(True)
                names = []
                for chn in range(channels):
                    main_names, sub_names = window._encode_resolution_choices(chn)
                    for name in (main_names if key.startswith("m") else sub_names):
                        if name not in names:
                            names.append(name)
                editor.addItems(names or list(ENCODE_RESOLUTIONS))
                if key == "s_res":
                    if editor.findText("HD1") < 0:
                        editor.addItem("HD1")
                    editor.setCurrentText("HD1")
            elif key.endswith("_fps"):
                editor = QSpinBox()
                editor.setRange(1, 30)
                editor.setValue(20 if key.startswith("m_") else 12)
            elif key.endswith("_rc"):
                editor = QComboBox()
                editor.addItems(ENCODE_RATE_CONTROL)
                editor.setCurrentText("VBR")
            elif key.endswith("_quality"):
                editor = QSpinBox()
                editor.setRange(1, 6)
                editor.setValue(4 if key.startswith("m_") else 3)
            elif key.endswith("_gop"):
                editor = QSpinBox()
                editor.setRange(1, 250)
                editor.setValue(2)
            else:
                editor = QComboBox()
                editor.setEditable(True)
                editor.addItems(["Off", "H265+", "H265AI"])
            self._all[key] = editor
            footer.setCellWidget(0, column, editor)
            button = QPushButton("To all")
            button.clicked.connect(
                lambda _=False, name=key: self._apply_all(name))
            footer.setCellWidget(1, column, button)
        table.resizeColumnsToContents()

        header = table.horizontalHeader()

        def sync_footer(*_):
            try:
                footer.verticalHeader().setFixedWidth(
                    table.verticalHeader().width())
                for column in range(len(self.KEYS)):
                    footer.setColumnWidth(column, header.sectionSize(column))
                footer.setFixedHeight(footer.rowHeight(0) + footer.rowHeight(1)
                                      + 2 * footer.frameWidth())
            except RuntimeError:
                return

        self._sync_footer = sync_footer
        header.sectionResized.connect(sync_footer)
        table.verticalHeader().geometriesChanged.connect(sync_footer)
        sync_footer()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self._apply)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(apply_button)
        buttons.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.addWidget(table, 1)
        layout.addWidget(footer)
        layout.addLayout(buttons)

    def showEvent(self, event):
        super().showEvent(event)
        self._sync_footer()

    def _apply_all(self, name):
        editor = self._all[name]
        for fields in self._rows.values():
            widget = fields[name]
            if not widget.isEnabled():
                continue
            if isinstance(widget, QComboBox):
                if widget.findText(editor.currentText()) < 0:
                    widget.addItem(editor.currentText())
                widget.setCurrentText(editor.currentText())
            else:
                widget.setValue(editor.value())

    def _apply(self):
        window = self._window
        for chn, fields in self._rows.items():
            entry = window._encode_entry(chn)
            if not isinstance(entry, dict):
                continue
            for prefix, format_key in (("m", "MainFormat"), ("s", "ExtraFormat")):
                fmt = entry.setdefault(format_key, {})
                if not isinstance(fmt, dict):
                    fmt = {}
                    entry[format_key] = fmt
                video = fmt.setdefault("Video", {})
                video["Resolution"] = fields[prefix + "_res"].currentText().strip()
                video["FPS"] = fields[prefix + "_fps"].value()
                video["BitRateControl"] = fields[prefix + "_rc"].currentText().strip()
                video["Quality"] = fields[prefix + "_quality"].value()
                video["GOP"] = fields[prefix + "_gop"].value()
                if video["BitRateControl"].upper() == "VBR":
                    bitrate = encode_vbr_bitrate(
                        video["Resolution"], video.get("Compression"),
                        video["Quality"], video["FPS"], video["GOP"],
                        window._encode_max_fps)
                    if bitrate:
                        video["BitRate"] = bitrate
            smart_state = window._encode_smart_state(chn)
            if isinstance(smart_state, dict):
                config = smart_state.get("config")
                if isinstance(config, dict):
                    for index, key in ((0, "m_smart"), (1, "s_smart")):
                        value = fields[key].currentText()
                        if smart_state.get("mode") == "v2":
                            plus = config.setdefault("Smart264PlusV2", [])
                            v2 = config.setdefault("Smart264V2", [])
                            while len(plus) <= index:
                                plus.append({})
                            while len(v2) <= index:
                                v2.append({})
                            if isinstance(plus[index], dict):
                                plus[index]["SmartH264Plus"] = (
                                    1 if value == "H265AI" else 0)
                            if isinstance(v2[index], dict):
                                v2[index]["SmartH264"] = value == "H265+"
                        elif smart_state.get("mode") == "v1" and index == 0:
                            config["SmartH264"] = value != "Off"
        channels = []
        for chn, config in enumerate(window._encode_configs):
            if isinstance(config, list) and config and isinstance(config[0], dict):
                channels.append((chn, config))
        if not channels:
            window._message("Nothing to apply.")
            return
        for key in ("encode_channels", "encode_smart", "encode_ability", "av_encode"):
            window._fetched_keys.discard(key)
        window._start_system_action(
            "apply",
            changes={"encode_channels": channels,
                     "encode_smart": window._encode_smart_changes()},
            label="Applying encode settings on")
        self.accept()


class SnapshotWindow(QDialog):
    """Popup that shows a NETIP snapshot; right-click to save it."""

    def __init__(self, image, data, default_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Snapshot")
        self.setModal(False)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self._image = image
        self._data = bytes(data)
        self._default_name = default_name

        shown = image
        screen = parent.screen() if parent is not None else QApplication.primaryScreen()
        if screen is not None:
            area = screen.availableGeometry()
            max_width = max(160, int(area.width() * 0.9))
            max_height = max(160, int(area.height() * 0.9))
            if image.width() > max_width or image.height() > max_height:
                shown = image.scaled(
                    max_width, max_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background-color: #101010;")
        self.label.setPixmap(QPixmap.fromImage(shown))
        self.label.setFixedSize(shown.size())
        self.label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.label.customContextMenuRequested.connect(self._context_menu)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setFixedSize(shown.size())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

    def _context_menu(self, point):
        menu = QMenu(self)
        save = menu.addAction("Save image...")
        save.triggered.connect(self._save)
        menu.exec(self.label.mapToGlobal(point))

    def _save(self):
        settings = QSettings("xmdm3", "xmdms")
        start_dir = str(settings.value("snapshot_dir", "", type=str) or "")
        if not start_dir:
            start_dir = os.path.expanduser("~")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save snapshot", os.path.join(start_dir, self._default_name),
            "JPEG image (*.jpg *.jpeg);;PNG image (*.png);;All files (*)")
        if not path:
            return
        _root, ext = os.path.splitext(path)
        if not ext:
            path += ".jpg"
            ext = ".jpg"
        try:
            if (ext.lower() in (".jpg", ".jpeg")
                    and self._data[:2] == b"\xff\xd8"):
                with open(path, "wb") as handle:
                    handle.write(self._data)
            elif not self._image.save(path):
                raise OSError("unsupported image format")
        except OSError as error:
            QMessageBox.warning(
                self, "Save snapshot", "Cannot save %s: %s" % (path, error))
            return
        settings.setValue("snapshot_dir", os.path.dirname(path))


class RecoveryDialog(QDialog):
    """Build an XM-DVR recovery image from a firmware zip."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recovery image")
        self.resize(560, 430)
        self._zip_path = ""
        self._entries = []

        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_button = QPushButton("Browse...")
        input_button.clicked.connect(self._pick_input)
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Firmware file:"))
        input_row.addWidget(self.input_edit, 1)
        input_row.addWidget(input_button)

        self.file_list = QListWidget()
        self.file_list.itemChanged.connect(self._update_summary)

        select_all = QPushButton("Select all")
        select_all.clicked.connect(lambda: self._set_all(True))
        select_none = QPushButton("Select none")
        select_none.clicked.connect(lambda: self._set_all(False))
        list_bar = QHBoxLayout()
        list_bar.addWidget(QLabel("Files to include:"))
        list_bar.addStretch(1)
        list_bar.addWidget(select_all)
        list_bar.addWidget(select_none)

        self.output_edit = QLineEdit()
        output_button = QPushButton("Save as...")
        output_button.clicked.connect(self._pick_output)
        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Output file:"))
        output_row.addWidget(self.output_edit, 1)
        output_row.addWidget(output_button)

        self.summary_label = QLabel("Pick a firmware zip to begin.")
        self.build_button = QPushButton("Build")
        self.build_button.clicked.connect(self._build)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        buttons = QHBoxLayout()
        buttons.addWidget(self.summary_label, 1)
        buttons.addWidget(self.build_button)
        buttons.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.addLayout(input_row)
        layout.addLayout(list_bar)
        layout.addWidget(self.file_list, 1)
        layout.addLayout(output_row)
        layout.addLayout(buttons)


    def _notify(self, text):
        self.summary_label.setText(text)
        parent = self.parent()
        if parent is not None and hasattr(parent, "_message"):
            parent._message(text)

    @staticmethod
    def _size(value):
        try:
            number = float(value)
        except (TypeError, ValueError):
            return str(value)
        for unit in ("B", "KiB", "MiB", "GiB"):
            if number < 1024 or unit == "GiB":
                if unit == "B":
                    return "%d %s" % (number, unit)
                return "%.1f %s" % (number, unit)
            number /= 1024.0
        return str(value)

    def _pick_input(self):
        settings = QSettings("xmdm3", "xmdms")
        start_dir = os.path.dirname(self._zip_path) or str(
            settings.value("firmware_dir", "", type=str) or "")
        path, _ = QFileDialog.getOpenFileName(
            self, "Select firmware file", start_dir,
            "Firmware files (*.bin);;All files (*)")
        if not path:
            return
        self._zip_path = path
        self.input_edit.setText(path)
        settings.setValue("firmware_dir", os.path.dirname(path))
        self.output_edit.setText(os.path.splitext(path)[0] + ".img")
        self._load_entries()

    def _load_entries(self):
        self.file_list.blockSignals(True)
        self.file_list.clear()
        self._entries = []
        error = None
        try:
            with zipfile.ZipFile(self._zip_path) as archive:
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    if not info.filename.lower().endswith(".img"):
                        continue
                    self._entries.append(info.filename)
                    item = QListWidgetItem("%s  (%s)" % (
                        info.filename, self._size(info.file_size)))
                    item.setFlags(
                        item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Checked)
                    item.setData(Qt.ItemDataRole.UserRole, info.filename)
                    self.file_list.addItem(item)
        except (OSError, zipfile.BadZipFile) as exc:
            error = exc
        self.file_list.blockSignals(False)
        self._update_summary()
        if error is not None:
            self._notify("Cannot read the firmware file")

    def _set_all(self, checked):
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        self.file_list.blockSignals(True)
        for index in range(self.file_list.count()):
            self.file_list.item(index).setCheckState(state)
        self.file_list.blockSignals(False)
        self._update_summary()

    def _selected(self):
        names = []
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                names.append(item.data(Qt.ItemDataRole.UserRole))
        return names

    def _update_summary(self, *_):
        total = self.file_list.count()
        if not total:
            self.summary_label.setText("No .img files found.")
            return
        self.summary_label.setText(
            "%d of %d file(s) selected" % (len(self._selected()), total))

    def _pick_output(self):
        start = self.output_edit.text().strip()
        if not start:
            base = os.path.splitext(os.path.basename(self._zip_path))[0] or "recovery"
            start = os.path.join(os.path.dirname(self._zip_path), base + ".img")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save recovery image", start,
            "Recovery image (*.img);;All files (*)")
        if path:
            self.output_edit.setText(path)

    def _build(self):
        output = self.output_edit.text().strip()
        if not self._zip_path or not os.path.isfile(self._zip_path):
            self._notify("Pick a firmware file first.")
            return
        if not output:
            self._notify("Choose an output file.")
            return
        names = self._selected()
        if not names:
            self._notify("Select at least one file to include.")
            return
        size = 0
        try:
            with zipfile.ZipFile(self._zip_path) as archive:
                with open(output, "wb+") as handle:
                    handle.write(b"\x00" * 64)
                    handle.seek(0)
                    handle.write(b"XM-DVR")
                    handle.seek(20)
                    handle.write(b"\x40")
                    handle.seek(64)
                    for name in names:
                        handle.write(archive.read(name))
                    size = handle.tell()
                    handle.seek(24)
                    handle.write(size.to_bytes(4, "little"))
        except (OSError, zipfile.BadZipFile, KeyError):
            self._notify("Recovery image failed")
            return
        self._notify("Recovery image written successfully")


class DumpDialog(QDialog):
    """Build a flat flash dump from the uImage files inside a firmware zip."""

    COLUMNS = ("", "#", "Name", "Load", "Entry", "Size")
    COL_CHECK = 0
    COL_NAME = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Firmware dump")
        self.resize(700, 470)
        self._zip_path = ""
        self._entries = {}

        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_button = QPushButton("Browse...")
        input_button.clicked.connect(self._pick_input)
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Firmware file:"))
        input_row.addWidget(self.input_edit, 1)
        input_row.addWidget(input_button)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 4096)
        self.size_spin.setValue(8)
        self.size_spin.setSuffix(" MB")
        self.size_spin.setMaximumWidth(100)
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Dump size:"))
        size_row.addWidget(self.size_spin)
        size_row.addStretch(1)

        self.file_table = QTableWidget(0, len(self.COLUMNS))
        self.file_table.setHorizontalHeaderLabels(self.COLUMNS)
        self.file_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.file_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.file_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection)
        self.file_table.setAlternatingRowColors(True)
        self.file_table.verticalHeader().setVisible(False)
        header = self.file_table.horizontalHeader()
        header.setStretchLastSection(False)
        metrics = self.file_table.fontMetrics()
        indicator = self.style().pixelMetric(
            QStyle.PixelMetric.PM_IndicatorWidth)
        fixed_widths = (
            (self.COL_CHECK, indicator + 10),
            (1, metrics.horizontalAdvance("99") + 12),
            (3, metrics.horizontalAdvance("0x00000000") + 12),
            (4, metrics.horizontalAdvance("0x00000000") + 12),
            (5, metrics.horizontalAdvance("8888.8 MiB") + 12),
        )
        for column, width in fixed_widths:
            header.setSectionResizeMode(
                column, QHeaderView.ResizeMode.Fixed)
            self.file_table.setColumnWidth(column, width)
        header.setSectionResizeMode(
            self.COL_NAME, QHeaderView.ResizeMode.Stretch)
        self.file_table.itemChanged.connect(self._update_summary)

        select_all = QPushButton("Select all")
        select_all.clicked.connect(lambda: self._set_all(True))
        select_none = QPushButton("Select none")
        select_none.clicked.connect(lambda: self._set_all(False))
        list_bar = QHBoxLayout()
        list_bar.addWidget(QLabel("Files to include:"))
        list_bar.addStretch(1)
        list_bar.addWidget(select_all)
        list_bar.addWidget(select_none)

        self.output_edit = QLineEdit()
        output_button = QPushButton("Save as...")
        output_button.clicked.connect(self._pick_output)
        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Output file:"))
        output_row.addWidget(self.output_edit, 1)
        output_row.addWidget(output_button)

        self.summary_label = QLabel("Pick a firmware file to begin.")
        self.build_button = QPushButton("Build")
        self.build_button.clicked.connect(self._build)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        buttons = QHBoxLayout()
        buttons.addWidget(self.summary_label, 1)
        buttons.addWidget(self.build_button)
        buttons.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.addLayout(input_row)
        layout.addLayout(size_row)
        layout.addLayout(list_bar)
        layout.addWidget(self.file_table, 1)
        layout.addLayout(output_row)
        layout.addLayout(buttons)

    def _notify(self, text):
        self.summary_label.setText(text)
        parent = self.parent()
        if parent is not None and hasattr(parent, "_message"):
            parent._message(text)

    @staticmethod
    def _size(value):
        try:
            number = float(value)
        except (TypeError, ValueError):
            return str(value)
        for unit in ("B", "KiB", "MiB"):
            if number < 1024 or unit == "MiB":
                if unit == "B":
                    return "%d %s" % (number, unit)
                return "%.1f %s" % (number, unit)
            number /= 1024.0
        return str(value)

    def _pick_input(self):
        settings = QSettings("xmdm3", "xmdms")
        start_dir = os.path.dirname(self._zip_path) or str(
            settings.value("firmware_dir", "", type=str) or "")
        path, _ = QFileDialog.getOpenFileName(
            self, "Select firmware file", start_dir,
            "Firmware files (*.bin);;All files (*)")
        if not path:
            return
        self._zip_path = path
        self.input_edit.setText(path)
        settings.setValue("firmware_dir", os.path.dirname(path))
        self.output_edit.setText(os.path.splitext(path)[0] + ".dump")
        self._load_entries()

    def _load_entries(self):
        table = self.file_table
        table.blockSignals(True)
        table.setRowCount(0)
        self._entries = {}
        error = None
        try:
            with zipfile.ZipFile(self._zip_path) as archive:
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    try:
                        data = archive.read(info.filename)
                    except (OSError, zipfile.BadZipFile):
                        continue
                    header = parse_uimage_header(data)
                    if header is None:
                        continue
                    self._entries[info.filename] = header
                    row = table.rowCount()
                    table.insertRow(row)
                    check = QTableWidgetItem()
                    check.setFlags(
                        Qt.ItemFlag.ItemIsUserCheckable
                        | Qt.ItemFlag.ItemIsEnabled
                        | Qt.ItemFlag.ItemIsSelectable)
                    check.setCheckState(Qt.CheckState.Checked)
                    check.setData(Qt.ItemDataRole.UserRole, info.filename)
                    table.setItem(row, self.COL_CHECK, check)
                    table.setItem(row, 1, QTableWidgetItem(str(row + 1)))
                    table.setItem(row, self.COL_NAME, QTableWidgetItem(info.filename))
                    table.setItem(row, 3, QTableWidgetItem(
                        "0x%08X" % header["load"]))
                    table.setItem(row, 4, QTableWidgetItem(
                        "0x%08X" % header["entry"]))
                    table.setItem(row, 5, QTableWidgetItem(
                        self._size(header["size"])))
        except (OSError, zipfile.BadZipFile) as exc:
            error = exc
        table.blockSignals(False)
        self._update_summary()
        if error is not None:
            self._notify("Cannot read the firmware file: %s" % error)

    def _set_all(self, checked):
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        table = self.file_table
        table.blockSignals(True)
        for row in range(table.rowCount()):
            item = table.item(row, self.COL_CHECK)
            if item is not None:
                item.setCheckState(state)
        table.blockSignals(False)
        self._update_summary()

    def _selected(self):
        table = self.file_table
        names = []
        for row in range(table.rowCount()):
            item = table.item(row, self.COL_CHECK)
            if item is not None and item.checkState() == Qt.CheckState.Checked:
                names.append(item.data(Qt.ItemDataRole.UserRole))
        return names

    def _required_mb(self):
        required = 0
        for name in self._selected():
            header = self._entries.get(name)
            if not header:
                continue
            required = max(required, header["load"] + header["size"])
        if not required:
            return 0
        return max(8, (required + (1 << 20) - 1) >> 20)

    def _bump_size(self, required_mb):
        if required_mb <= self.size_spin.value():
            return
        target = None
        for step in DUMP_SIZE_STEPS:
            if step >= required_mb:
                target = step
                break
        if target is None:
            target = min(4096, ((required_mb + 1023) // 1024) * 1024)
        self.size_spin.setValue(target)

    def _update_summary(self, *_):
        total = self.file_table.rowCount()
        if not total:
            self.summary_label.setText("No uImage files found.")
            return
        required = self._required_mb()
        self._bump_size(required)
        self.summary_label.setText(
            "%d of %d file(s) selected (need %d MB)" % (
                len(self._selected()), total, required))

    def _pick_output(self):
        start = self.output_edit.text().strip()
        if not start:
            base = os.path.splitext(os.path.basename(self._zip_path))[0] or "dump"
            start = os.path.join(os.path.dirname(self._zip_path), base + ".dump")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save dump", start, "Dump image (*.dump);;All files (*)")
        if path:
            self.output_edit.setText(path)

    def _build(self):
        output = self.output_edit.text().strip()
        if not self._zip_path or not os.path.isfile(self._zip_path):
            self._notify("Pick a firmware file first.")
            return
        if not output:
            self._notify("Choose an output file.")
            return
        names = self._selected()
        if not names:
            self._notify("Select at least one file to include.")
            return
        self._bump_size(self._required_mb())
        size_mb = self.size_spin.value()
        dump = bytearray(size_mb * 1024 * 1024)
        written = 0
        skipped = []
        try:
            with zipfile.ZipFile(self._zip_path) as archive:
                for name in names:
                    data = archive.read(name)
                    header = parse_uimage_header(data)
                    if header is None:
                        skipped.append(name)
                        continue
                    payload = bytes(data[UIMAGE_HEADER_SIZE:
                                         UIMAGE_HEADER_SIZE + header["size"]])
                    offset = header["load"]
                    if offset + len(payload) > len(dump):
                        skipped.append(name)
                        continue
                    dump[offset:offset + len(payload)] = payload
                    written += 1
        except (OSError, zipfile.BadZipFile):
            self._notify("Dump failed: cannot read the firmware file")
            return
        if not written:
            self._notify("Dump failed: nothing to write")
            return
        try:
            with open(output, "wb") as handle:
                handle.write(dump)
        except OSError:
            self._notify("Dump failed: cannot write the output file")
            return
        if skipped:
            self._notify("Dump written successfully (%d skipped)" % len(skipped))
        else:
            self._notify("Dump written successfully")


class ResetConfigDialog(QDialog):
    FIELDS = (
        ("General", "General"),
        ("Encode", "Encode"),
        ("Record", "Record"),
        ("Alarm", "Alarm"),
        ("Network", "NetCommon"),
        ("NetServer", "NetServer"),
        ("GUI display", "Preview"),
        ("Account", "Account"),
        ("RS232", "CommPtz"),
        ("Camera param", "CameraPARAM"),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reset config")
        self.full_reset = False
        self.checks = {}
        self.all_check = QCheckBox("Select all")
        self.all_check.toggled.connect(self._toggle_all)
        grid = QGridLayout()
        for index, (label, key) in enumerate(self.FIELDS):
            check = QCheckBox(label)
            self.checks[key] = check
            grid.addWidget(check, index // 2, index % 2)
        selected_button = QPushButton("Reset selected")
        full_button = QPushButton("Factory Reset")
        cancel_button = QPushButton("Cancel")
        selected_button.clicked.connect(self._accept_selected)
        full_button.clicked.connect(self._accept_full)
        cancel_button.clicked.connect(self.reject)
        buttons = QHBoxLayout()
        buttons.addWidget(selected_button)
        buttons.addWidget(full_button)
        buttons.addStretch(1)
        buttons.addWidget(cancel_button)
        layout = QVBoxLayout(self)
        layout.addWidget(self.all_check)
        layout.addLayout(grid)
        layout.addLayout(buttons)

    def _toggle_all(self, checked):
        for check in self.checks.values():
            check.setChecked(checked)

    def _accept_selected(self):
        self.full_reset = False
        self.accept()

    def _accept_full(self):
        self.full_reset = True
        self.accept()

    def payload(self):
        config = {
            "CameraPARAM": False, "CommPtz": False, "Record": False,
            "Encode": False, "XMModeSwitch": False, "RestoreDefaultConfig": False,
            "RestoreFactoryConfig": False, "Account": False, "Alarm": False,
            "General": False, "NetCommon": False, "NetServer": False,
            "Preview": False,
        }
        if self.full_reset:
            for key in ("CameraPARAM", "CommPtz", "Record", "Encode",
                        "XMModeSwitch", "RestoreDefaultConfig",
                        "RestoreFactoryConfig", "Alarm", "General", "NetServer",
                        "Preview"):
                config[key] = True
            config["Account"] = False
            config["NetCommon"] = False
        else:
            for key, check in self.checks.items():
                config[key] = check.isChecked()
        return config


class DigNetworkDialog(QDialog):
    """Edit the network settings of an IPC found through the NVR search."""

    def __init__(self, device, username="admin", password="", parent=None):
        super().__init__(parent)
        address = format_ipv4(device.get("HostIP"))
        self.setWindowTitle("Network settings — %s" % (address or "device"))
        self.address_edit = IpAddressEdit()
        self.address_edit.setValue(address)
        self.submask_edit = IpAddressEdit()
        self.submask_edit.setValue(
            format_ipv4(device.get("Submask")) or "255.255.255.0")
        gateway = format_ipv4(device.get("GateWay"))
        if not gateway and address:
            gateway = address.rsplit(".", 1)[0] + ".1"
        self.gateway_edit = IpAddressEdit()
        self.gateway_edit.setValue(gateway)
        self.user_edit = QLineEdit(username or "admin")
        self.password_edit = QLineEdit(password or "")
        configure_password_edit(self.password_edit)

        form = QGridLayout()
        rows = (
            ("IP address:", self.address_edit),
            ("Subnet mask:", self.submask_edit),
            ("Gateway:", self.gateway_edit),
            ("Login:", self.user_edit),
            ("Password:", self.password_edit),
        )
        for row, (label, widget) in enumerate(rows):
            form.addWidget(QLabel(label), row, 0)
            form.addWidget(widget, row, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def accept(self):
        if not (self.address_edit.value() and self.submask_edit.value()
                and self.gateway_edit.value()):
            QMessageBox.warning(
                self, "Network settings",
                "Enter a valid IP address, subnet mask and gateway.")
            return
        super().accept()

    def values(self):
        return {
            "address": self.address_edit.value(),
            "submask": self.submask_edit.value(),
            "gateway": self.gateway_edit.value(),
            "username": self.user_edit.text().strip() or "admin",
            "password": self.password_edit.text(),
        }


class DigitalChannelsDialog(QDialog):
    SEARCH_COLUMNS = ("Set", "IP", "Mask", "Gateway", "Port", "MAC", "SN",
                      "Host Name", "Channels", "Type")
    CHANNEL_COLUMNS = ("On", "Name", "IP", "Port", "SyncRes", "SyncTime",
                       "Prio", "Ch", "Protocol", "User", "Password",
                       "CfgName")
    CHANNEL_WIDTHS = (40, 130, 110, 60, 60, 80, 55, 40, 80, 80, 100, 130)
    DEVICE_TYPES = {305201157: "NVR", 305201156: "DVR", 7: "IPC WiFi", 4: "NVR", 0: "IPC"}
    SYNC_TIME_OPTIONS = ("OFF", "T&Z", "Local", "UTC")
    DELAY_OPTIONS = (150, 250, 333, 667, 1000, 2000, 3000)
    PROTOCOL_OPTIONS = ("NETIP", "ONVIF", "RTSP")
    DELAY_DEFAULT = 333
    COL_ON = 0
    COL_NAME = 1
    COL_IP = 2
    COL_PORT = 3
    COL_SYNC_RES = 4
    COL_SYNC_TIME = 5
    COL_DELAY = 6
    COL_CHANNEL = 7
    COL_PROTOCOL = 8
    COL_USER = 9
    COL_PASSWORD = 10
    COL_CONFNAME = 11
    NUMBER_ATTEMPTS = 2

    def __init__(self, device, username, password, parent=None):
        super().__init__(parent)
        self._address = device.get("ip") or ""
        self._cloud_id = device.get("cloud_id") or ""
        self._rps = bool(device.get("rps", True))
        self._no_md5 = bool(device.get("no_md5"))
        self._port = int(device.get("tcp_port") or 34567)
        self._username = username
        self._password = password
        self._thread = None
        self._local_devices = []
        self._search_checked = set()
        self._remote_entries = []
        self._titles = []
        self._time_syn = []
        self._decode_param = []
        self._reload_pending = False
        self._subnet = str(device.get("subnet") or "")
        self._gateway = str(device.get("gateway") or "")
        self._prov_queue = []
        self._prov_active = False
        self._prov_attempts = {}
        self._prov_total = 0
        self._prov_done = 0
        self._prov_failed = 0
        self._prov_current = None

        self.setWindowTitle("Digital channels — %s" % (self._cloud_id or self._address))
        self.resize(1080, 680)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._search_local)
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(("NETIP", "ONVIF"))
        self.search_type_combo.currentIndexChanged.connect(self._refresh_local_table)
        self.add_ipc_button = QPushButton("Add all IPC")
        self.add_ipc_button.clicked.connect(self._add_all_ipc)
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_channels)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        self.provision_ip_edit = IpAddressEdit()
        self.provision_ip_edit.setToolTip(
            "First IP to assign. Set automatically to the selected channel IP + 1; "
            "can be edited manually.")
        self.provision_button = QPushButton("Provision IP")
        self.provision_button.setToolTip(
            "Set IPs for checked devices in the search list (or checked Set "
            "channels), starting from Start IP. Two attempts per device.")
        self.provision_button.clicked.connect(self._provision_ips)
        self.provision_status = QLabel("")

        self.search_table = self._make_table(self.SEARCH_COLUMNS)
        self.search_table.verticalHeader().setVisible(True)
        self.search_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self.search_table.customContextMenuRequested.connect(
            self._search_context_menu)
        self.search_table.itemChanged.connect(self._on_search_item_changed)
        self.search_table.itemSelectionChanged.connect(self._on_search_selection)

        search_panel = QWidget()
        search_layout = QVBoxLayout(search_panel)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.addWidget(self.search_table, 1)

        self.channel_table = QTableWidget(0, len(self.CHANNEL_COLUMNS))
        self.channel_table.setHorizontalHeaderLabels(self.CHANNEL_COLUMNS)
        install_copy_menu(self.channel_table)
        self.channel_table.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.EditKeyPressed)
        self.channel_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.channel_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.channel_table.setAlternatingRowColors(True)
        vertical = self.channel_table.verticalHeader()
        vertical.setSectionsMovable(True)
        vertical.setAcceptDrops(True)
        vertical.sectionMoved.connect(self._renumber_channels)
        header = self.channel_table.horizontalHeader()
        for column, width in enumerate(self.CHANNEL_WIDTHS):
            header.resizeSection(column, width)
        text_width = self.fontMetrics().averageCharWidth() * 10 + 16
        header.resizeSection(self.COL_USER, text_width)
        header.resizeSection(self.COL_PASSWORD, text_width)

        middle_bar = QHBoxLayout()
        middle_bar.addWidget(self.search_button)
        middle_bar.addWidget(QLabel("Search type:"))
        middle_bar.addWidget(self.search_type_combo)
        middle_bar.addWidget(self.add_ipc_button)
        middle_bar.addWidget(QLabel("Start IP:"))
        middle_bar.addWidget(self.provision_ip_edit)
        middle_bar.addWidget(self.provision_button)
        middle_bar.addWidget(self.provision_status, 1)

        channel_panel = QWidget()
        channel_layout = QVBoxLayout(channel_panel)
        channel_layout.setContentsMargins(0, 0, 0, 0)
        channel_layout.addLayout(middle_bar)
        channel_layout.addWidget(self.channel_table, 1)
        channel_layout.addLayout(self._build_apply_panel())

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(search_panel)
        splitter.addWidget(channel_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([240, 400])

        layout = QVBoxLayout(self)
        layout.addWidget(splitter, 1)

        self._start("remote_devices", self._on_remote_devices)

    def _build_apply_panel(self):
        self.username_input = QLineEdit("admin")
        self.password_input = QLineEdit()
        configure_password_edit(self.password_input)
        self.name_input = QLineEdit("CAM")
        self.protocol_input = QComboBox()
        self.protocol_input.addItems(self.PROTOCOL_OPTIONS)
        self.syncres_input = QComboBox()
        self.syncres_input.addItems(("Disabled", "Enabled"))
        self.syncres_input.setCurrentText("Disabled")
        self.synctime_input = QComboBox()
        self.synctime_input.addItems(self.SYNC_TIME_OPTIONS)
        self.synctime_input.setCurrentText("Local")
        self.delay_input = QComboBox()
        self.delay_input.addItems([str(value) for value in self.DELAY_OPTIONS])
        self.delay_input.setCurrentText(str(self.DELAY_DEFAULT))
        self.subnet_input = QLineEdit()
        self.subnet_input.setPlaceholderText("192.168.1")
        self.subnet_input.setToolTip(
            "To All replaces the first three octets of each channel IP, "
            "keeping that channel's last octet (e.g. 192.168.1).")

        fields = (
            ("User:", self.username_input,
             lambda: self._apply_text(self.COL_USER, self.username_input.text())),
            ("Password:", self.password_input,
             lambda: self._apply_text(self.COL_PASSWORD, self.password_input.text())),
            ("Channel name:", self.name_input,
             lambda: self._apply_names(self.name_input.text())),
            ("Protocol:", self.protocol_input,
             lambda: self._apply_combo(self.COL_PROTOCOL, self.protocol_input.currentText())),
            ("Sync res:", self.syncres_input,
             lambda: self._apply_check(
                 self.COL_SYNC_RES,
                 self.syncres_input.currentText() == "Enabled")),
            ("Sync time:", self.synctime_input,
             lambda: self._apply_combo(self.COL_SYNC_TIME, self.synctime_input.currentText())),
            ("Delay decode:", self.delay_input,
             lambda: self._apply_combo(self.COL_DELAY, self.delay_input.currentText())),
            ("Subnet:", self.subnet_input,
             lambda: self._apply_subnet()),
        )
        width = self.fontMetrics().averageCharWidth() * 10 + 20
        for widget in (self.username_input, self.password_input, self.name_input,
                       self.protocol_input, self.syncres_input,
                       self.synctime_input, self.delay_input, self.subnet_input):
            widget.setFixedWidth(width)
        grid = QGridLayout()
        for column, (label, widget, handler) in enumerate(fields):
            grid.addWidget(QLabel(label), 0, column)
            grid.addWidget(widget, 1, column)
            button = QPushButton("To All")
            button.setFixedWidth(width)
            button.clicked.connect(handler)
            grid.addWidget(button, 2, column)
        grid.setColumnStretch(len(fields), 1)
        grid.addWidget(self.apply_button, 2, len(fields) + 1)
        grid.addWidget(self.close_button, 2, len(fields) + 2)
        return grid

    @staticmethod
    def _make_table(columns):
        table = QTableWidget(0, len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        return table

    @staticmethod
    def _text(value):
        return "" if value is None else str(value)

    @staticmethod
    def _decoder(entry):
        decoder = entry.get("Decoder") if isinstance(entry, dict) else None
        if isinstance(decoder, dict):
            return decoder
        if isinstance(decoder, list) and decoder and isinstance(decoder[0], dict):
            return decoder[0]
        return None

    def _start(self, action, handler, changes=None, on_failed=None):
        if self._thread is not None:
            return
        thread = NetipThread(
            action, self._address, self._username, self._password,
            cloud_id=self._cloud_id, rps=self._rps, changes=changes,
            port=self._port, parent=self, no_md5=self._no_md5)
        thread.fetched.connect(handler)
        thread.applied.connect(handler)
        thread.failed.connect(on_failed or self._on_failed)
        thread.finished.connect(self._on_finished)
        self._thread = thread
        self.search_button.setEnabled(False)
        self.apply_button.setEnabled(False)
        thread.start()

    @staticmethod
    def _error_text(ret):
        if ret is None:
            return "no reply code"
        return "%s (Ret=%s)" % (RESULT_CODES.get(ret, "error"), ret)

    @staticmethod
    def _is_auth_failure(text):
        lowered = str(text or "").lower()
        if any("ret=%d" % code in lowered for code in AUTH_ERROR_CODES):
            return True
        return any(hint in lowered for hint in AUTH_ERROR_HINTS)

    @staticmethod
    def _is_timeout_failure(text):
        lowered = str(text or "").lower()
        if any("ret=%d" % code in lowered for code in TIMEOUT_ERROR_CODES):
            return True
        return any(hint in lowered for hint in TIMEOUT_ERROR_HINTS)

    def _on_failed(self, text):
        if self._prov_active and self._prov_current is not None:
            if self._is_auth_failure(text):
                self._provision_failed(self._prov_current, text)
            else:
                self._provision_retry(self._prov_current, text)
            return
        QMessageBox.warning(self, "Digital channels", text)

    def _on_finished(self):
        thread = self._thread
        self._thread = None
        if thread is not None:
            thread.deleteLater()
        self.search_button.setEnabled(True)
        self.apply_button.setEnabled(True)
        if self._prov_active:
            self._start_next_provision()
            return
        if self._reload_pending:
            self._reload_pending = False
            self._start("remote_devices", self._on_remote_devices)

    def _search_local(self):
        self._start(
            "local_search", self._on_local_devices,
            changes={"protocol": self.search_type_combo.currentText()})

    def _on_remote_devices(self, payload):
        devices = payload.get("remote_devices")
        if not isinstance(devices, list):
            QMessageBox.warning(self, "Digital channels",
                                "Unexpected reply for NetWork.RemoteDeviceV3.")
            return
        self._remote_entries = devices
        titles = payload.get("channel_titles")
        self._titles = titles if isinstance(titles, list) else []
        time_syn = payload.get("time_syn")
        self._time_syn = time_syn if isinstance(time_syn, list) else []
        decode_param = payload.get("decode_param")
        self._decode_param = decode_param if isinstance(decode_param, list) else []
        table = self.channel_table
        table.setUpdatesEnabled(False)
        table.setRowCount(len(devices))
        for row, entry in enumerate(devices):
            if not isinstance(entry, dict):
                entry = {}
            decoder = self._decoder(entry) or {}
            title = self._titles[row] if row < len(self._titles) else None
            time_syn_value = self._entry_value(self._time_syn, row, "TimeSyn")
            delay_value = self._entry_value(self._decode_param, row, "deleyTimeMs")
            self._fill_channel_row(row, entry, decoder, title, time_syn_value, delay_value)
        table.setUpdatesEnabled(True)
        self._renumber_channels()
        if not self.subnet_input.text().strip():
            for row in range(table.rowCount()):
                address = self._cell_text(row, self.COL_IP)
                octets = address.split(".")
                if len(octets) == 4:
                    self.subnet_input.setText(".".join(octets[:3]))
                    break
        self._refresh_local_table()

    @staticmethod
    def _entry_value(entries, row, key):
        if row < len(entries) and isinstance(entries[row], dict):
            return entries[row].get(key)
        return None

    def _fill_channel_row(self, row, entry, decoder, title=None, time_syn=None, delay=None):
        self._set_check_item(row, self.COL_ON, bool(entry.get("Enable")))
        self._set_text_item(row, self.COL_NAME, title or decoder.get("ConfName") or "CAM")
        self._set_text_item(row, self.COL_IP, decoder.get("IPAddress"))
        self._set_text_item(row, self.COL_PORT, decoder.get("Port"))
        self._set_check_item(row, self.COL_SYNC_RES, not bool(entry.get("SynchResolution")))
        self._set_combo_item(
            row, self.COL_SYNC_TIME, self.SYNC_TIME_OPTIONS,
            self._text(time_syn or "OFF"))
        self._set_combo_item(
            row, self.COL_DELAY, [str(value) for value in self.DELAY_OPTIONS],
            self._text(delay if delay is not None else self.DELAY_DEFAULT))
        self._set_text_item(
            row, self.COL_CHANNEL, self._channel_label(decoder.get("Channel")))
        self._set_combo_item(
            row, self.COL_PROTOCOL, self.PROTOCOL_OPTIONS,
            self._text(decoder.get("Protocol") or "NETIP"))
        self._set_text_item(row, self.COL_USER, decoder.get("UserName") or "admin")
        self._set_text_item(row, self.COL_PASSWORD, decoder.get("PassWord") or "")
        self._set_text_item(row, self.COL_CONFNAME, decoder.get("ConfName"))

    @staticmethod
    def _channel_label(value):
        """Show the zero-based channel as a human 1-based number."""
        try:
            return str(int(value) + 1)
        except (TypeError, ValueError):
            return "" if value is None else str(value)

    def _set_text_item(self, row, column, value):
        item = QTableWidgetItem(self._text(value))
        item.setFlags(
            Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable)
        self.channel_table.setItem(row, column, item)

    def _set_check_item(self, row, column, checked):
        if column in (self.COL_ON, self.COL_SYNC_RES):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addStretch(1)
            box = QCheckBox()
            box.setChecked(bool(checked))
            layout.addWidget(box)
            layout.addStretch(1)
            self.channel_table.setCellWidget(row, column, container)
            return
        item = QTableWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        self.channel_table.setItem(row, column, item)

    def _set_combo_item(self, row, column, options, current):
        combo = QComboBox()
        combo.addItems(options)
        index = combo.findText(current)
        if index >= 0:
            combo.setCurrentIndex(index)
        self.channel_table.setCellWidget(row, column, combo)

    def _item(self, row, column):
        item = self.channel_table.item(row, column)
        if item is None:
            item = QTableWidgetItem()
            self.channel_table.setItem(row, column, item)
        return item

    def _renumber_channels(self, *_):
        header = self.channel_table.verticalHeader()
        for row in range(self.channel_table.rowCount()):
            item = self.channel_table.verticalHeaderItem(row)
            if item is None:
                item = QTableWidgetItem()
                self.channel_table.setVerticalHeaderItem(row, item)
            item.setText(str(header.visualIndex(row) + 1))

    def _apply_text(self, column, text):
        for row in range(self.channel_table.rowCount()):
            self._item(row, column).setText(text)

    def _apply_names(self, prefix):
        header = self.channel_table.verticalHeader()
        count = self.channel_table.rowCount()
        digits = max(2, len(str(count)))
        for row in range(count):
            position = header.visualIndex(row) + 1
            self._item(row, self.COL_NAME).setText("%s%0*d" % (prefix, digits, position))

    def _apply_check(self, column, checked):
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for row in range(self.channel_table.rowCount()):
            widget = self.channel_table.cellWidget(row, column)
            box = widget.findChild(QCheckBox) if widget is not None else None
            if box is not None:
                box.setChecked(bool(checked))
            else:
                self._item(row, column).setCheckState(state)

    def _apply_subnet(self):
        text = self.subnet_input.text().strip().rstrip(".")
        octets = text.split(".")
        if (len(octets) != 3
                or not all(part.isdigit() and 0 <= int(part) <= 255
                           for part in octets)):
            self.provision_status.setText(
                "Subnet must be three octets, e.g. 192.168.1")
            return
        prefix = ".".join(str(int(part)) for part in octets)
        changed = 0
        for row in range(self.channel_table.rowCount()):
            address = self._cell_text(row, self.COL_IP)
            parts = address.split(".")
            if len(parts) != 4 or not parts[3].isdigit():
                continue
            self._item(row, self.COL_IP).setText(
                "%s.%s" % (prefix, parts[3]))
            changed += 1
        self.provision_status.setText(
            "Subnet changed for %d channel(s)." % changed)

    def _apply_combo(self, column, text):
        for row in range(self.channel_table.rowCount()):
            combo = self.channel_table.cellWidget(row, column)
            if combo is None:
                continue
            index = combo.findText(text)
            if index >= 0:
                combo.setCurrentIndex(index)

    def _on_local_devices(self, payload):
        devices = payload.get("local_search")
        if not isinstance(devices, list):
            QMessageBox.warning(self, "Digital channels",
                                "Unexpected reply for NetLocalSearch.")
            return
        self._local_devices = [device for device in devices if isinstance(device, dict)]
        self._refresh_local_table()

    @staticmethod
    def _is_xiongmai(device):
        return device.get("Manufacturer") == 4

    def _filtered_local_devices(self):
        return list(self._local_devices)

    @staticmethod
    def _search_key(device):
        mac = str(device.get("MAC") or "").strip().lower()
        if mac:
            return mac
        address = format_ipv4(device.get("HostIP"))
        if address:
            return address
        return str(device.get("SN") or "").strip()

    def _channel_device_keys(self):
        """MACs and IPs already present in the channel list."""
        macs = set()
        addresses = set()
        for row in range(self.channel_table.rowCount()):
            entry = self._remote_entries[row] if row < len(self._remote_entries) else {}
            decoder = self._decoder(entry) or {}
            mac = str(decoder.get("MacAddr") or "").strip().lower()
            if mac:
                macs.add(mac)
            address = self._cell_text(row, self.COL_IP).strip()
            if address:
                addresses.add(address)
        return macs, addresses

    def _refresh_local_table(self, *_):
        devices = self._filtered_local_devices()
        added_macs, added_addresses = self._channel_device_keys()
        self.search_table.setSortingEnabled(False)
        self.search_table.setRowCount(len(devices))
        for row, device in enumerate(devices):
            key = self._search_key(device)
            check = QTableWidgetItem()
            check.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable)
            check.setCheckState(
                Qt.CheckState.Checked if key in self._search_checked
                else Qt.CheckState.Unchecked)
            check.setData(Qt.ItemDataRole.UserRole, key)
            self.search_table.setItem(row, 0, check)
            values = (
                format_ipv4(device.get("HostIP")),
                format_ipv4(device.get("Submask")),
                format_ipv4(device.get("GateWay")),
                self._text(device.get("TCPPort")),
                self._text(device.get("MAC")),
                self._text(device.get("SN")),
                self._text(device.get("HostName")),
                self._text(device.get("ChannelNum")),
                self.DEVICE_TYPES.get(device.get("DeviceType"), self._text(device.get("DeviceType"))),
            )
            mac = str(device.get("MAC") or "").strip().lower()
            address = format_ipv4(device.get("HostIP"))
            already_added = bool((mac and mac in added_macs)
                                 or (address and address in added_addresses))
            for column, value in enumerate(values, start=1):
                item = QTableWidgetItem(value)
                if already_added:
                    item.setForeground(QBrush(QColor("#9E9E9E")))
                    item.setToolTip("Already in the channels list")
                self.search_table.setItem(row, column, item)
            if already_added:
                check.setToolTip("Already in the channels list")
        self.search_table.resizeColumnsToContents()
        address_width = (
            self.search_table.fontMetrics().horizontalAdvance("255.255.255.255") + 24)
        header = self.search_table.horizontalHeader()
        for column in (1, 2, 3):
            header.resizeSection(
                column, max(header.sectionSize(column), address_width))
        self.search_table.setSortingEnabled(True)

    def _on_search_item_changed(self, item):
        if item is None or item.column() != 0:
            return
        key = item.data(Qt.ItemDataRole.UserRole)
        if not key:
            return
        if item.checkState() == Qt.CheckState.Checked:
            self._search_checked.add(key)
        else:
            self._search_checked.discard(key)

    def _on_search_selection(self):
        rows = self.search_table.selectionModel().selectedRows()
        if not rows:
            return
        item = self.search_table.item(rows[0].row(), 0)
        key = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        for device in self._local_devices:
            if self._search_key(device) == key:
                self.provision_ip_edit.setValue(
                    next_ip_address(format_ipv4(device.get("HostIP"))))
                break

    def _search_device_row(self, key):
        for row in range(self.search_table.rowCount()):
            item = self.search_table.item(row, 0)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == key:
                return row
        return None

    def _set_search_row_brush(self, key, brush):
        row = self._search_device_row(key)
        if row is None:
            return
        for column in range(self.search_table.columnCount()):
            item = self.search_table.item(row, column)
            if item is not None:
                item.setBackground(brush if brush is not None else QBrush())

    def _channel_row_for_device(self, device):
        mac = str(device.get("MAC") or "").strip().lower()
        address = format_ipv4(device.get("HostIP"))
        if mac:
            for row in range(self.channel_table.rowCount()):
                entry = self._remote_entries[row] if row < len(self._remote_entries) else {}
                decoder = self._decoder(entry) or {}
                if str(decoder.get("MacAddr") or "").strip().lower() == mac:
                    return row
        if address:
            for row in range(self.channel_table.rowCount()):
                if self._cell_text(row, self.COL_IP) == address:
                    return row
        return None

    def _add_all_ipc(self):
        added_macs, added_addresses = self._channel_device_keys()
        for device in self._filtered_local_devices():
            if device.get("DeviceType") not in (0, 7):
                continue
            address = format_ipv4(device.get("HostIP"))
            if not address:
                continue
            mac = str(device.get("MAC") or "").strip().lower()
            if (mac and mac in added_macs) or address in added_addresses:
                continue
            if not self._append_ipc_channel(device):
                break
            if mac:
                added_macs.add(mac)
            added_addresses.add(address)
        self._refresh_local_table()

    def _device_by_search_key(self, key):
        for device in self._local_devices:
            if self._search_key(device) == key:
                return device
        return None

    def _search_context_menu(self, point):
        index = self.search_table.indexAt(point)
        if not index.isValid():
            return
        item = self.search_table.item(index.row(), 0)
        key = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        device = self._device_by_search_key(key)
        value = table_cell_text(self.search_table, index)
        menu = QMenu(self.search_table)
        copy_action = menu.addAction("Copy")
        copy_action.setEnabled(bool(value))
        copy_action.triggered.connect(
            lambda: QApplication.clipboard().setText(value))
        menu.addSeparator()
        add_action = menu.addAction("Add to channels")
        add_action.setEnabled(device is not None)
        add_action.triggered.connect(
            lambda: self._add_search_device(device))
        network_action = menu.addAction("Change network settings...")
        network_action.setEnabled(device is not None)
        network_action.triggered.connect(
            lambda: self._edit_search_device_network(device))
        menu.exec(self.search_table.viewport().mapToGlobal(point))

    def _add_search_device(self, device):
        if not isinstance(device, dict):
            return
        if not self._append_ipc_channel(device):
            self.provision_status.setText(
                "No empty channel slot available.")
            return
        self._refresh_local_table()
        self.provision_status.setText(
            "Added %s to channels" % (format_ipv4(device.get("HostIP"))))

    def _edit_search_device_network(self, device):
        if not isinstance(device, dict):
            return
        dialog = DigNetworkDialog(
            device, self.username_input.text().strip() or "admin",
            self.password_input.text(), self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._send_search_device_network(device, dialog.values())

    def _send_search_device_network(self, device, values):
        row = self._channel_row_for_device(device)
        entry = (self._remote_entries[row]
                 if row is not None and row < len(self._remote_entries) else {})
        decoder = self._decoder(entry) or {}
        mac = (str(device.get("MAC") or "").strip()
               or str(decoder.get("MacAddr") or "").strip())
        hostname = str(device.get("HostName") or "").strip()
        netcfg = {
            "GateWay": format_ip_set(values["gateway"]),
            "HostIP": format_ip_set(values["address"]),
            "Submask": format_ip_set(values["submask"]),
            "MAC": mac,
            "TCPPort": self._to_int(device.get("TCPPort"), 34567),
            "HttpPort": self._to_int(device.get("HttpPort"), 80),
        }
        if hostname:
            netcfg["HostName"] = hostname
        channel = (self.channel_table.verticalHeader().visualIndex(row) + 1
                   if row is not None else 0)
        payload = {
            "Name": "OPDIGSetIP",
            "OPDIGSetIP": {
                "Channel": channel,
                "devtype": "IPC",
                "LoginCfg": {
                    "UserName": values["username"],
                    "EncryptType": 1,
                    "Password": sofia_hash(values["password"]),
                },
                "Netcfg": netcfg,
            },
        }
        self._start(
            "dig_set_ip",
            lambda result, dev=device, vals=values:
            self._on_search_network_result(dev, vals, result),
            changes={"payload": payload},
            on_failed=lambda text, dev=device:
            self._on_search_network_failed(dev, text))

    def _on_search_network_failed(self, device, text):
        brush = (PROVISION_ACTIVE_BRUSH if self._is_timeout_failure(text)
                 else PROVISION_FAILED_BRUSH)
        self._set_search_row_brush(self._search_key(device), brush)
        self.provision_status.setText("Network change failed: %s" % text)

    def _on_search_network_result(self, device, values, payload):
        reply = payload.get("OPDIGSetIP") if isinstance(payload, dict) else None
        ret = reply.get("Ret") if isinstance(reply, dict) else None
        if ret != 100:
            reason = self._error_text(ret)
            brush = (PROVISION_ACTIVE_BRUSH if self._is_timeout_failure(reason)
                     else PROVISION_FAILED_BRUSH)
            self._set_search_row_brush(self._search_key(device), brush)
            self.provision_status.setText(
                "Network change failed: %s" % reason)
            return
        device["HostIP"] = values["address"]
        device["Submask"] = values["submask"]
        device["GateWay"] = values["gateway"]
        self._refresh_local_table()
        self._set_search_row_brush(
            self._search_key(device), PROVISION_OK_BRUSH)
        self.provision_status.setText(
            "Network settings applied: %s" % values["address"])

    def _append_ipc_channel(self, device):
        table = self.channel_table
        row = None
        for candidate in range(table.rowCount()):
            if not self._cell_text(candidate, self.COL_IP):
                row = candidate
                break
        if row is None:
            return False
        host = self._text(device.get("HostName")).strip() or "CAM"
        prefix = self.name_input.text().strip() or "CAM"
        count = table.rowCount()
        digits = max(2, len(str(count)))
        position = table.verticalHeader().visualIndex(row) + 1
        name = "%s%0*d" % (prefix, digits, position)
        if self.search_type_combo.currentText() == "ONVIF" or not self._is_xiongmai(device):
            protocol = "ONVIF"
        else:
            protocol = "NETIP"
        self._set_check_item(row, self.COL_ON, True)
        self._set_text_item(row, self.COL_NAME, name)
        self._set_text_item(row, self.COL_IP, format_ipv4(device.get("HostIP")))
        self._set_text_item(row, self.COL_PORT, self._text(device.get("TCPPort") or 34567))
        self._set_check_item(row, self.COL_SYNC_RES, False)
        self._set_combo_item(row, self.COL_SYNC_TIME, self.SYNC_TIME_OPTIONS, "Local")
        self._set_combo_item(
            row, self.COL_DELAY, [str(value) for value in self.DELAY_OPTIONS],
            str(self.DELAY_DEFAULT))
        self._set_text_item(row, self.COL_CHANNEL, "1")
        self._set_combo_item(row, self.COL_PROTOCOL, self.PROTOCOL_OPTIONS, protocol)
        self._set_text_item(row, self.COL_USER, "admin")
        self._set_text_item(row, self.COL_PASSWORD, "")
        self._set_text_item(row, self.COL_CONFNAME, host)
        self._titles[row] = name
        self._time_syn[row] = "Local"
        self._decode_param[row] = self.DELAY_DEFAULT
        self._renumber_channels()
        return True

    def _cell_text(self, row, column):
        item = self.channel_table.item(row, column)
        return item.text().strip() if item is not None else ""

    def _cell_checked(self, row, column):
        widget = self.channel_table.cellWidget(row, column)
        box = widget.findChild(QCheckBox) if widget is not None else None
        if box is not None:
            return box.isChecked()
        item = self.channel_table.item(row, column)
        return item is not None and item.checkState() == Qt.CheckState.Checked

    def _combo_text(self, row, column):
        combo = self.channel_table.cellWidget(row, column)
        return combo.currentText() if combo is not None else ""

    @staticmethod
    def _to_int(text, default):
        try:
            return int(str(text).strip())
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _merge_row_entries(base, values_by_row, key, rows):
        """Merge fetched per-row values into base entries, following row moves."""
        merged = []
        for row in rows:
            entry = dict(base[row]) if row < len(base) and isinstance(base[row], dict) else {}
            entry[key] = values_by_row.get(row)
            merged.append(entry)
        for entry in base[len(rows):]:
            merged.append(entry)
        return merged

    def _channel_config(self):
        table = self.channel_table
        header = table.verticalHeader()
        config = []
        titles = []
        time_syn_by_row = {}
        decode_param_by_row = {}
        rows = []
        for visual in range(table.rowCount()):
            row = header.logicalIndex(visual)
            rows.append(row)
            base = self._remote_entries[row] if row < len(self._remote_entries) else {}
            entry = dict(base) if isinstance(base, dict) else {}
            on = self._cell_checked(row, self.COL_ON)
            entry["Enable"] = on
            entry["SynchResolution"] = not self._cell_checked(row, self.COL_SYNC_RES)
            entry.pop("TimeSyn", None)
            entry.pop("deleyTimeMs", None)
            titles.append(self._cell_text(row, self.COL_NAME))
            time_syn_by_row[row] = self._combo_text(row, self.COL_SYNC_TIME)
            decode_param_by_row[row] = self._to_int(
                self._combo_text(row, self.COL_DELAY), self.DELAY_DEFAULT)
            entry.setdefault("ConnType", "SINGLE")
            entry.setdefault("EnCheckTime", True)
            entry.setdefault("SingleConnId", "0x00000001")
            entry.setdefault("TourIntv", 10)
            ip = self._cell_text(row, self.COL_IP)
            decoder = dict(self._decoder(base) or {})
            if not ip and not decoder:
                entry["Decoder"] = None
            else:
                protocol = self._combo_text(row, self.COL_PROTOCOL)
                decoder["ConfName"] = self._cell_text(row, self.COL_CONFNAME)
                decoder["IPAddress"] = ip
                decoder["Port"] = self._to_int(
                    self._cell_text(row, self.COL_PORT), 34567)
                channel_text = self._cell_text(row, self.COL_CHANNEL).strip()
                try:
                    decoder["Channel"] = max(0, int(channel_text) - 1)
                except (TypeError, ValueError):
                    decoder["Channel"] = 0
                decoder["UserName"] = self._cell_text(row, self.COL_USER) or "admin"
                decoder["PassWord"] = self._cell_text(row, self.COL_PASSWORD)
                decoder["Protocol"] = "TCP" if protocol == "NETIP" else protocol
                decoder["Enable"] = on
                decoder.setdefault("DevType", "IPC")
                decoder.setdefault("Interval", 10)
                decoder.setdefault("MacAddr", "")
                decoder.setdefault("MainRtspUrl", "")
                decoder.setdefault("SerialNo", "")
                decoder.setdefault("StreamType", "MAIN")
                decoder.setdefault("SubRtspUrl", "")
                decoder.setdefault("TransModel", 0)
                entry["Decoder"] = [decoder]
            config.append(entry)
        time_syn = self._merge_row_entries(
            self._time_syn, time_syn_by_row, "TimeSyn", rows)
        decode_param = self._merge_row_entries(
            self._decode_param, decode_param_by_row, "deleyTimeMs", rows)
        return {
            "channels": config,
            "titles": titles + list(self._titles[table.rowCount():]),
            "time_syn": time_syn,
            "decode_param": decode_param,
        }

    @staticmethod
    def _valid_ip(value, fallback):
        try:
            ipaddress.IPv4Address(str(value or "").strip())
        except (ipaddress.AddressValueError, ValueError):
            return fallback
        return str(value).strip()

    @staticmethod
    def _dig_netcfg(new_ip, mac, hostname, tcp_port, http_port, subnet, gateway):
        netcfg = {
            "GateWay": format_ip_set(gateway),
            "HostIP": format_ip_set(new_ip),
            "Submask": format_ip_set(subnet),
            "MAC": mac,
            "TCPPort": tcp_port,
            "HttpPort": http_port,
        }
        if hostname:
            netcfg["HostName"] = hostname
        return netcfg

    @staticmethod
    def _dig_set_ip_payload(channel, devtype, username, password, netcfg):
        return {
            "Name": "OPDIGSetIP",
            "OPDIGSetIP": {
                "Channel": channel,
                "devtype": devtype,
                "LoginCfg": {
                    "UserName": username,
                    "EncryptType": 1,
                    "Password": sofia_hash(password),
                },
                "Netcfg": netcfg,
            },
        }

    @staticmethod
    def _gateway_on_subnet(new_ip, subnet, gateway):
        """Keep the gateway in new_ip's subnet, preserving its host bits."""
        try:
            network = ipaddress.IPv4Network(
                "%s/%s" % (new_ip, subnet), strict=False)
        except (ipaddress.AddressValueError, ValueError):
            return gateway
        try:
            old = ipaddress.IPv4Address(str(gateway or "").strip())
        except (ipaddress.AddressValueError, ValueError):
            old = None
        if old is not None and old in network:
            return str(old)
        host = (int(old) & ~int(network.netmask)) if old is not None else 1
        base = int(network.network_address)
        for offset in (host, 1, 254, 2):
            value = base + offset
            if value > 0xFFFFFFFF:
                continue
            candidate = ipaddress.IPv4Address(value)
            if (candidate in network
                    and candidate != network.network_address
                    and candidate != network.broadcast_address
                    and candidate != ipaddress.IPv4Address(new_ip)):
                return str(candidate)
        return gateway

    def _dig_defaults(self, new_ip):
        subnet = self._valid_ip(self._subnet, "255.255.255.0")
        gateway = self._valid_ip(
            self._gateway, new_ip.rsplit(".", 1)[0] + ".1")
        return subnet, self._gateway_on_subnet(new_ip, subnet, gateway)

    def _build_dig_ip_payload_for_device(self, device, new_ip, row):
        entry = (self._remote_entries[row]
                 if row is not None and row < len(self._remote_entries) else {})
        decoder = self._decoder(entry) or {}
        mac = (str(device.get("MAC") or "").strip()
               or str(decoder.get("MacAddr") or "").strip())
        username = (self.username_input.text().strip()
                    or str(decoder.get("UserName") or "") or "admin")
        password = (self.password_input.text()
                    or str(decoder.get("PassWord") or ""))
        hostname = str(device.get("HostName") or "").strip()
        if not hostname:
            hostname = str(decoder.get("HostName") or "").strip()
        if not hostname and row is not None:
            hostname = self._cell_text(row, self.COL_CONFNAME)
        tcp_port = device.get("TCPPort") or decoder.get("Port") or 34567
        http_port = decoder.get("HttpPort") or 80
        devtype = str(decoder.get("DevType") or "IPC")
        subnet, gateway = self._dig_defaults(new_ip)
        netcfg = self._dig_netcfg(
            new_ip, mac, hostname, self._to_int(tcp_port, 34567),
            self._to_int(http_port, 80), subnet, gateway)
        channel = (self.channel_table.verticalHeader().visualIndex(row) + 1
                   if row is not None else 0)
        return self._dig_set_ip_payload(
            channel, devtype, username, password, netcfg)

    def _jobs_from_search(self, base_value):
        devices = [device for device in self._local_devices
                   if self._search_key(device) in self._search_checked
                   and format_ipv4(device.get("HostIP"))]
        jobs = []
        for offset, device in enumerate(devices):
            value = base_value + offset
            if value > 0xFFFFFFFF:
                break
            address = str(ipaddress.IPv4Address(value))
            key = self._search_key(device)
            jobs.append({
                "row": self._channel_row_for_device(device),
                "device": device,
                "search_key": key,
                "key": ("search", key, address),
                "ip": address,
            })
        return jobs

    def _provision_ips(self):
        if self._prov_active or self._thread is not None:
            self.provision_status.setText("Another operation is running.")
            return
        base = self.provision_ip_edit.value()
        if not base:
            self.provision_status.setText("Set a valid Start IP first.")
            return
        base_value = int(ipaddress.IPv4Address(base))
        jobs = self._jobs_from_search(base_value)
        if not jobs:
            self.provision_status.setText(
                "Check devices in the search list first.")
            return
        self._prov_queue = jobs
        self._prov_total = len(jobs)
        self._prov_done = 0
        self._prov_failed = 0
        self._prov_attempts = {}
        self._prov_active = True
        for job in jobs:
            self._set_search_row_brush(
                job["search_key"], PROVISION_ACTIVE_BRUSH)
        self.provision_button.setEnabled(False)
        self.provision_status.setText(
            "Provisioning %d device(s) from %s ..." % (self._prov_total, base))
        self._start_next_provision()

    def _start_next_provision(self):
        if not self._prov_queue:
            self._prov_active = False
            self._prov_current = None
            self.provision_button.setEnabled(True)
            self.provision_status.setText(
                "Provisioning done: %d ok, %d failed." % (
                    self._prov_done, self._prov_failed))
            return
        job = self._prov_queue.pop(0)
        self._prov_current = job
        key = job["key"]
        self._prov_attempts[key] = self._prov_attempts.get(key, 0) + 1
        self._set_search_row_brush(job["search_key"], PROVISION_ACTIVE_BRUSH)
        payload = self._build_dig_ip_payload_for_device(
            job["device"], job["ip"], job["row"])
        self._start(
            "dig_set_ip",
            lambda result, current=job: self._on_provision_reply(current, result),
            changes={"payload": payload})

    def _on_provision_reply(self, job, payload):
        reply = payload.get("OPDIGSetIP") if isinstance(payload, dict) else None
        ret = reply.get("Ret") if isinstance(reply, dict) else None
        if ret != 100:
            reason = self._error_text(ret)
            if self._is_auth_failure(reason):
                self._provision_failed(job, reason)
            else:
                self._provision_retry(job, reason)
            return
        self._prov_done += 1
        device = job["device"]
        search_key = job["search_key"]
        if isinstance(device, dict):
            device["HostIP"] = job["ip"]
            new_key = self._search_key(device)
            if search_key and new_key != search_key:
                self._search_checked.discard(search_key)
                self._search_checked.add(new_key)
            row_search = self._search_device_row(search_key)
            if row_search is not None:
                check = self.search_table.item(row_search, 0)
                if check is not None:
                    check.setData(Qt.ItemDataRole.UserRole, new_key)
                cell = self.search_table.item(row_search, 1)
                if cell is not None:
                    cell.setText(job["ip"])
            self._set_search_row_brush(new_key, PROVISION_OK_BRUSH)
        self.provision_status.setText(
            "Provisioned %s" % (job["ip"]))

    def _provision_retry(self, job, reason):
        attempts = self._prov_attempts.get(job["key"], 0)
        label = job["search_key"]
        if attempts < self.NUMBER_ATTEMPTS:
            self._prov_queue.append(job)
            self.provision_status.setText(
                "%s failed (%s) — retry %d/%d ..." % (
                    label, reason, attempts + 1, self.NUMBER_ATTEMPTS))
        else:
            self._provision_failed(
                job, reason, timeout=self._is_timeout_failure(reason))

    def _provision_failed(self, job, reason, timeout=False):
        """Finish a provisioning job: red for errors, yellow for timeouts."""
        self._prov_failed += 1
        brush = PROVISION_ACTIVE_BRUSH if timeout else PROVISION_FAILED_BRUSH
        self._set_search_row_brush(job["search_key"], brush)
        self.provision_status.setText(
            "%s %s: %s" % (job["search_key"],
                           "timed out" if timeout else "failed", reason))

    def _apply_channels(self):
        self._start(
            "set_remote_devices", self._on_applied, changes=self._channel_config())

    def _on_applied(self, payload):
        failures = []
        for name, reply in payload.items():
            ret = reply.get("Ret") if isinstance(reply, dict) else None
            if ret != 100:
                failures.append("%s Ret=%s (%s)" % (
                    name, ret, RESULT_CODES.get(ret, "unknown")))
        if failures:
            QMessageBox.warning(self, "Digital channels",
                                "Apply failed: " + ", ".join(failures))
            return
        self._reload_pending = True

    def showEvent(self, event):
        super().showEvent(event)
        screen = self.screen()
        if screen is None:
            return
        available = screen.availableGeometry()
        frame = max(0, self.frameGeometry().height() - self.height())
        self.resize(self.width(), max(self.minimumHeight(),
                                      available.height() - frame))
        geometry = self.frameGeometry()
        x = min(max(geometry.x(), available.left()),
                max(available.left(),
                    available.right() - geometry.width() + 1))
        self.move(x, available.top())

    def closeEvent(self, event):
        self._prov_active = False
        self._prov_current = None
        thread = self._thread
        self._thread = None
        if thread is not None:
            thread.wait(10000)
            thread.deleteLater()
        super().closeEvent(event)


def alaw_to_linear(value):
    value ^= 0x55
    sign = value & 0x80
    exponent = (value & 0x70) >> 4
    mantissa = value & 0x0F
    sample = mantissa << 4
    if exponent == 0:
        sample += 8
    elif exponent == 1:
        sample += 0x108
    else:
        sample += 0x108
        sample <<= exponent - 1
    return sample if sign else -sample


ALAW_TABLE = tuple(alaw_to_linear(value) for value in range(256))


class LiveStreamDevice(QIODevice):
    """QIODevice that blocks until the NETIP thread feeds more elementary data."""

    MAX_BUFFER = 4 * 1024 * 1024

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buffer = bytearray()
        self._condition = threading.Condition()
        self._ended = False

    def feed(self, data):
        with self._condition:
            self._buffer.extend(data)
            overflow = len(self._buffer) - self.MAX_BUFFER
            if overflow > 0:
                del self._buffer[:overflow]
            self._condition.notify_all()

    def end(self):
        with self._condition:
            self._ended = True
            self._buffer.clear()
            self._condition.notify_all()

    def reset(self):
        with self._condition:
            self._buffer.clear()
            self._ended = False
            self._condition.notify_all()

    def clear(self):
        with self._condition:
            self._buffer.clear()
            self._condition.notify_all()

    def isSequential(self):
        return True

    def atEnd(self):
        with self._condition:
            return self._ended and not self._buffer

    def bytesAvailable(self):
        with self._condition:
            return len(self._buffer) + super().bytesAvailable()

    def readData(self, maxlen):
        with self._condition:
            if not self._buffer and not self._ended:
                self._condition.wait(0.25)
            if not self._buffer:
                return b""
            data = bytes(self._buffer[:maxlen])
            del self._buffer[:maxlen]
            return data

    def writeData(self, data):
        return 0


class G711AudioPlayer(QObject):
    """Plays G.711A NETIP audio through QAudioSink (push mode)."""

    SAMPLE_RATE = 8000

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sink = None
        self._stream = None
        self._written = 0
        self._pending = bytearray()
        self._sink_failed = False
        self._volume = 0.8
        self._muted = True

    def feed(self, data):
        if not data:
            return
        pcm = bytearray(len(data) * 2)
        for index, value in enumerate(data):
            sample = ALAW_TABLE[value]
            pcm[index * 2] = sample & 0xFF
            pcm[index * 2 + 1] = (sample >> 8) & 0xFF
        if self._sink is None:
            if self._sink_failed:
                return
            self._pending.extend(pcm)
            limit = self.SAMPLE_RATE * 8
            if len(self._pending) > limit:
                del self._pending[:len(self._pending) - limit]
            if len(self._pending) < self.SAMPLE_RATE:
                return
            self._start_sink()
            if self._sink is None or self._stream is None:
                self._sink_failed = True
                self._pending.clear()
                return
            chunk = bytes(self._pending)
            self._pending.clear()
            self._written += len(chunk)
            self._stream.write(chunk)
            return
        processed = self._sink.processedUSecs()
        if processed >= 0:
            played = processed * self.SAMPLE_RATE * 2 // 1000000
            if self._written - played > self.SAMPLE_RATE * 4:
                return
        self._written += len(pcm)
        self._stream.write(bytes(pcm))

    def _start_sink(self):
        if not QT_MULTIMEDIA:
            return
        output = QMediaDevices.defaultAudioOutput()
        if output is None:
            return
        fmt = QAudioFormat()
        fmt.setSampleRate(self.SAMPLE_RATE)
        fmt.setChannelCount(1)
        fmt.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        if not output.isFormatSupported(fmt):
            preferred = output.preferredFormat()
            if (preferred.sampleRate() != self.SAMPLE_RATE
                    or preferred.sampleFormat() != QAudioFormat.SampleFormat.Int16
                    or preferred.channelCount() != 1):
                return
            fmt = preferred
        self._sink = QAudioSink(output, fmt, self)
        self._sink.setBufferSize(self.SAMPLE_RATE * 2)
        self._sink.setVolume(0.0 if self._muted else self._volume)
        self._written = 0
        self._stream = self._sink.start()

    def set_volume(self, value):
        self._volume = max(0.0, min(1.0, value))
        if self._sink is not None:
            self._sink.setVolume(0.0 if self._muted else self._volume)

    def set_muted(self, muted):
        self._muted = bool(muted)
        if self._sink is not None:
            self._sink.setVolume(0.0 if self._muted else self._volume)

    def stop(self):
        if self._sink is not None:
            self._sink.stop()
            self._sink.deleteLater()
        self._sink = None
        self._stream = None
        self._pending.clear()
        self._sink_failed = False


class PyAvDecoder(QObject):
    """Optional fallback: decode H.264/H.265 with PyAV (if installed)."""

    image_ready = Signal(object)
    failed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._condition = threading.Condition()
        self._queue = deque()
        self._stop = True
        self._thread = None
        self.generation = 0
        self.codec = None

    def reset(self):
        with self._condition:
            self._queue.clear()
            self.codec = None

    def restart(self):
        with self._condition:
            self.generation += 1
            self._queue.clear()
            self.codec = None

    def feed(self, data, codec):
        with self._condition:
            if self._stop:
                self._stop = False
                self._thread = threading.Thread(target=self._run, daemon=True)
                self._thread.start()
            self._queue.append((bytes(data), codec))
            self._condition.notify_all()

    def stop(self):
        with self._condition:
            self._stop = True
            self._queue.clear()
            self._condition.notify_all()
        thread = self._thread
        self._thread = None
        if thread is not None:
            thread.join(2.0)

    def _run(self):
        context = None
        current = None
        while True:
            with self._condition:
                while not self._queue and not self._stop:
                    self._condition.wait(0.5)
                if self._stop and not self._queue:
                    return
                data, codec = self._queue.popleft()
            if codec and codec != current:
                name = {"h265": "hevc"}.get(codec, codec)
                try:
                    context = av.CodecContext.create(name, "r")
                except Exception as error:
                    self.failed.emit("PyAV: %s" % error)
                    context = None
                current = codec
            if context is None:
                continue
            try:
                for packet in context.parse(data):
                    for frame in context.decode(packet):
                        rgb = frame.reformat(format="rgb24")
                        plane = rgb.planes[0]
                        image = QImage(
                            bytes(plane), rgb.width, rgb.height, plane.line_size,
                            QImage.Format.Format_RGB888).copy()
                        self.image_ready.emit(image)
            except Exception as error:
                self.failed.emit("PyAV: %s" % error)


class StreamRecorder(QObject):
    """Write the raw NETIP elementary stream to disk while playing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._handle = None
        self._path = ""
        self._bytes = 0
        self._wait_keyframe = False
        self._lock = threading.Lock()

    def start(self, path, wait_keyframe=True):
        self.stop()
        try:
            handle = open(path, "wb")
        except OSError as error:
            return error
        with self._lock:
            self._handle = handle
            self._path = path
            self._bytes = 0
            self._wait_keyframe = bool(wait_keyframe)
        return None

    @property
    def is_recording(self):
        with self._lock:
            return self._handle is not None

    def feed(self, data, keyframe=False):
        with self._lock:
            handle = self._handle
            if handle is None:
                return
            if self._wait_keyframe:
                if not keyframe:
                    return
                self._wait_keyframe = False
            try:
                handle.write(data)
            except OSError:
                self._close_locked()
                return
            self._bytes += len(data)

    def stop(self):
        with self._lock:
            return self._close_locked()

    def _close_locked(self):
        handle = self._handle
        self._handle = None
        path = self._path
        size = self._bytes
        if handle is not None:
            try:
                handle.close()
            except OSError:
                pass
        if path:
            return path, size
        return None


FOCUS_WIDTH = 320
FOCUS_HEIGHT = 180
FOCUS_INTERVAL = 0.35
FOCUS_MIN_DETAIL = 6.0
FOCUS_LOG_DIVISOR = 5.0


def analyze_focus(image):
    """Return four quadrant sharpness scores (0-100) and an overall score.

    The score is based on the variance of the Laplacian on a downscaled
    grayscale image.  Low-detail regions return ``None`` instead of a
    misleading score: a blank wall has no focus signal to measure.
    """
    empty = [None, None, None, None]
    if not isinstance(image, QImage) or image.isNull():
        return empty, None, False
    small = image.scaled(
        FOCUS_WIDTH, FOCUS_HEIGHT,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation)
    gray = small.convertToFormat(QImage.Format.Format_Grayscale8)
    if gray.isNull():
        return empty, None, False
    width, height = gray.width(), gray.height()
    stride = gray.bytesPerLine()
    data = memoryview(gray.bits())
    scores = []
    for top, bottom in ((0, height // 2), (height // 2, height)):
        for left, right in ((0, width // 2), (width // 2, width)):
            lap_sum = 0
            lap_sq = 0
            gray_sum = 0
            gray_sq = 0
            count = 0
            for y in range(max(1, top + 1), min(height - 1, bottom - 1)):
                row = y * stride
                for x in range(max(1, left + 1), min(width - 1, right - 1)):
                    index = row + x
                    value = data[index]
                    lap = (4 * value - data[index - 1] - data[index + 1]
                           - data[index - stride] - data[index + stride])
                    lap_sum += lap
                    lap_sq += lap * lap
                    gray_sum += value
                    gray_sq += value * value
                    count += 1
            if count == 0:
                scores.append(None)
                continue
            mean_lap = lap_sum / count
            variance = max(0.0, lap_sq / count - mean_lap * mean_lap)
            mean_gray = gray_sum / count
            gray_variance = max(
                0.0, gray_sq / count - mean_gray * mean_gray)
            if math.sqrt(gray_variance) < FOCUS_MIN_DETAIL:
                scores.append(None)
                continue
            score = round(
                100.0 * math.log10(1.0 + variance) / FOCUS_LOG_DIVISOR)
            scores.append(max(0, min(100, int(score))))
    valid = [score for score in scores if score is not None]
    overall = round(sum(valid) / len(valid)) if valid else None
    return scores, overall, not valid


class FocusOverlay(QWidget):
    """Transparent four-zone sharpness overlay drawn over the video."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scores = [None, None, None, None]
        self._overall = None
        self._low_detail = False
        self._frame_size = None
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.hide()

    def set_frame_size(self, size):
        self._frame_size = tuple(size) if size else None
        self.update()

    def set_scores(self, scores, overall, low_detail=False):
        values = list(scores or [])
        values = (values + [None, None, None, None])[:4]
        self._scores = values
        self._overall = overall
        self._low_detail = bool(low_detail)
        self.update()

    def clear(self):
        self._scores = [None, None, None, None]
        self._overall = None
        self._low_detail = False
        self.update()

    def _content_rect(self):
        rect = self.rect()
        if not self._frame_size:
            return rect
        frame_width, frame_height = self._frame_size
        if frame_width <= 0 or frame_height <= 0:
            return rect
        scale = min(
            rect.width() / float(frame_width),
            rect.height() / float(frame_height))
        width = max(1, int(frame_width * scale))
        height = max(1, int(frame_height * scale))
        return QRect(
            rect.left() + (rect.width() - width) // 2,
            rect.top() + (rect.height() - height) // 2,
            width, height)

    @staticmethod
    def _score_color(score):
        if score is None:
            return QColor(210, 210, 210, 190)
        if score >= 70:
            return QColor(76, 175, 80, 235)
        if score >= 45:
            return QColor(255, 193, 7, 235)
        return QColor(244, 67, 54, 235)

    def paintEvent(self, _event):
        rect = self._content_rect().adjusted(4, 4, -4, -4)
        if rect.width() < 80 or rect.height() < 60:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        banner_font = self.font()
        banner_font.setBold(True)
        banner_font.setPixelSize(max(11, min(18, rect.height() // 24)))
        painter.setFont(banner_font)
        metrics = painter.fontMetrics()
        if self._low_detail:
            text = tr("Low detail — use a target")
        elif self._overall is None:
            text = tr("Analyzing focus...")
        else:
            text = "%s %d" % (tr("Focus"), self._overall)
        text = metrics.elidedText(
            text, Qt.TextElideMode.ElideRight, max(60, rect.width() - 32))
        banner_width = min(
            rect.width() - 8, metrics.horizontalAdvance(text) + 24)
        banner_height = metrics.height() + 10
        banner = QRect(
            rect.left() + (rect.width() - banner_width) // 2,
            rect.top(), banner_width, banner_height)
        painter.setPen(QPen(QColor(255, 255, 255, 150), 1))
        painter.setBrush(QColor(0, 0, 0, 155))
        painter.drawRoundedRect(banner, 6, 6)
        painter.setPen(QColor(255, 255, 255, 235))
        painter.drawText(
            banner, Qt.AlignmentFlag.AlignCenter, text)

        gap = max(4, rect.height() // 60)
        left = rect.left()
        top = rect.top() + banner_height + gap
        width = rect.width()
        height = max(1, rect.bottom() - top + 1)
        cell_width = max(1, (width - gap) // 2)
        cell_height = max(1, (height - gap) // 2)
        cells = (
            QRect(left, top, cell_width, cell_height),
            QRect(left + cell_width + gap, top, cell_width, cell_height),
            QRect(left, top + cell_height + gap, cell_width, cell_height),
            QRect(left + cell_width + gap, top + cell_height + gap,
                  cell_width, cell_height),
        )

        score_font = self.font()
        score_font.setBold(True)
        score_font.setPixelSize(
            max(18, min(48, int(cell_height * 0.30))))
        painter.setFont(score_font)
        for cell, score in zip(cells, self._scores):
            color = self._score_color(score)
            painter.setPen(QPen(QColor(color.red(), color.green(),
                                      color.blue(), 190), 2))
            painter.setBrush(QColor(0, 0, 0, 38))
            painter.drawRect(cell)
            label = "--" if score is None else str(score)
            shadow = cell.adjusted(1, 1, 1, 1)
            painter.setPen(QColor(0, 0, 0, 190))
            painter.drawText(
                shadow, Qt.AlignmentFlag.AlignCenter, label)
            painter.setPen(color)
            painter.drawText(
                cell, Qt.AlignmentFlag.AlignCenter, label)
        painter.end()


class VideoView(QGraphicsView):
    """QGraphicsView-based video surface that supports widget overlays."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setBackgroundBrush(QColor(16, 16, 16))
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setScene(QGraphicsScene(self))
        self.video_item = QGraphicsVideoItem()
        self.video_item.setAspectRatioMode(
            Qt.AspectRatioMode.KeepAspectRatio)
        self.scene().addItem(self.video_item)
        self.video_item.nativeSizeChanged.connect(self._fit_video)

    def _fit_video(self, *_args):
        size = self.video_item.nativeSize()
        if size.isEmpty():
            return
        if self.video_item.size() != size:
            self.video_item.setSize(size)
        rect = self.video_item.boundingRect()
        if rect.isEmpty():
            return
        self.setSceneRect(rect)
        self.fitInView(
            self.video_item, Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit_video()


class VideoPanel(QWidget):
    status_changed = Signal(str)
    keyframe = Signal()
    notice = Signal(str)
    lost = Signal(str)
    frame_in = Signal(object, object, object)
    jpeg_in = Signal(object)
    audio_in = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        self._image = None
        self._frame_size = None
        self._last_frame_time = 0.0
        self._focus_last = 0.0
        self._stream = "Main"
        self._channel = 0
        self._device = None
        self._username = "admin"
        self._password = ""
        self._decoded = 0
        self._switch_target = None
        self._switch_mark = 0
        self._switch_deadline = 0.0
        self._switch_timer = QTimer(self)
        self._switch_timer.setInterval(250)
        self._switch_timer.timeout.connect(self._check_switch)
        self._source_dirty = True
        self._qt_codec = None
        self._fallback_started = False
        self._active = False
        self._media_generation = 0
        self._retired_devices = []
        self._preroll_active = False
        self._preroll_frames = []
        self._preroll_keyframe = b""
        self._preroll_timer = QTimer(self)
        self._preroll_timer.setSingleShot(True)
        self._preroll_timer.timeout.connect(self._flush_preroll)
        self._preroll_feed_timer = QTimer(self)
        self._preroll_feed_timer.setInterval(20)
        self._preroll_feed_timer.timeout.connect(self._feed_preroll)
        self.codec = None
        self._backend = self._choose_backend()

        self.video_label = QLabel("no video")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(320, 180)
        self.video_label.setStyleSheet("background-color: #101010; color: #808080;")
        self.video_view = VideoView() if QT_MULTIMEDIA else None
        self._stack = QStackedWidget()
        self._stack.addWidget(self.video_label)
        if self.video_view is not None:
            self.video_view.setMinimumSize(320, 180)
            self._stack.addWidget(self.video_view)

        self.mute_check = QCheckBox("Mute")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(30)
        self.volume_slider.setFixedWidth(90)
        self.mute_check.toggled.connect(self._on_mute)
        self.volume_slider.valueChanged.connect(self._on_volume)

        self.record_button = QPushButton("REC")
        self.record_button.setCheckable(True)
        self.record_button.setToolTip(
            "Save the incoming stream to a file while watching.")
        self.record_button.toggled.connect(self._toggle_recording)
        self.record_label = QLabel("")
        self.record_label.setStyleSheet(
            "color: #C62828; font-weight: bold;")
        self._recorder = StreamRecorder(self)

        self.focus_button = QPushButton("Focus")
        self.focus_button.setCheckable(True)
        self.focus_button.setEnabled(False)
        self.focus_button.setToolTip(
            "Show focus sharpness scores for four regions. "
            "Point the camera at a detailed scene.")
        self.focus_button.toggled.connect(self._toggle_focus)

        controls = QHBoxLayout()
        controls.setContentsMargins(2, 0, 2, 0)
        controls.addWidget(self.mute_check)
        controls.addWidget(self.volume_slider)
        controls.addSpacing(8)
        controls.addWidget(self.record_button)
        controls.addWidget(self.record_label)
        controls.addWidget(self.focus_button)
        controls.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._stack, 1)
        layout.addLayout(controls)
        self.focus_overlay = FocusOverlay(self)
        self.focus_overlay.hide()

        self._stream_device = None
        self._player = QMediaPlayer(self) if QT_MULTIMEDIA else None
        if self._player is not None and self.video_view is not None:
            self._player.setVideoOutput(self.video_view.video_item)
            self._player.errorOccurred.connect(self._on_qt_error)
            self._player.mediaStatusChanged.connect(self._on_qt_media_status)
            sink = self._player.videoSink()
            if sink is not None:
                sink.videoFrameChanged.connect(self._on_video_frame)
        self._decoder = MjpegDecoder(self)
        self._decoder.frame_ready.connect(self._on_frame)
        self._decoder.failed.connect(self._on_decoder_failed)
        self._av_decoder = PyAvDecoder(self) if AV_AVAILABLE else None
        if self._av_decoder is not None:
            self._av_decoder.image_ready.connect(self._on_image)
            self._av_decoder.failed.connect(self._on_decoder_failed)
        self._audio = G711AudioPlayer(self) if QT_MULTIMEDIA else None
        self.mute_check.setChecked(True)
        self._watchdog = QTimer(self)
        self._watchdog.setSingleShot(True)
        self._watchdog.timeout.connect(self._watchdog_fired)

        self.frame_in.connect(self._handle_frame_in)
        self.jpeg_in.connect(self._handle_jpeg_in)
        self.audio_in.connect(self._handle_audio_in)

    @staticmethod
    def available():
        return QT_MULTIMEDIA or AV_AVAILABLE or MjpegDecoder.available()

    @staticmethod
    def _choose_backend():
        override = os.environ.get("XMDM_VIDEO_BACKEND", "").strip().lower()
        if override == "qt" and QT_MULTIMEDIA:
            return "qt"
        if override == "av" and AV_AVAILABLE:
            return "av"
        if override == "ffmpeg" and MjpegDecoder.available():
            return "ffmpeg"
        if QT_MULTIMEDIA:
            return "qt"
        if AV_AVAILABLE:
            return "av"
        return "ffmpeg"

    # -- sink protocol used by NetipVideoThread (worker thread) ------------

    def restart(self):
        self._source_dirty = True
        if self._backend == "ffmpeg":
            self._decoder.restart()
        elif self._backend == "av" and self._av_decoder is not None:
            self._av_decoder.restart()

    def feed(self, data, codec, keyframe=False):
        if codec:
            self.codec = codec
        self._decoded += 1
        self.frame_in.emit(bytes(data), codec, bool(keyframe))

    def push_jpeg(self, data, keyframe=False):
        self._decoded += 1
        self.jpeg_in.emit(bytes(data))

    def feed_audio(self, data):
        self.audio_in.emit(bytes(data))

    # -- queued handlers (GUI thread) --------------------------------------

    def _handle_frame_in(self, data, codec, keyframe=False):
        if not self._active:
            return
        self._recorder.feed(data, keyframe)
        if self._backend == "qt":
            if self._player is None:
                return
            if self._source_dirty or (codec and codec != self._qt_codec):
                self._source_dirty = False
                if codec:
                    self._qt_codec = codec
                self._restart_qt_source()
                if keyframe:
                    self._begin_preroll(data)
            if self._preroll_active:
                self._preroll_frames.append(bytes(data))
                return
            if self._stream_device is not None:
                self._stream_device.feed(data)
        elif self._backend == "av" and self._av_decoder is not None:
            self._av_decoder.feed(data, codec)
        else:
            self._decoder.feed(data, codec)

    def _handle_jpeg_in(self, data):
        if not self._active:
            return
        self._recorder.feed(data, True)
        image = QImage.fromData(data, "JPG")
        if image.isNull():
            return
        self._show_image(image)

    def _handle_audio_in(self, data):
        if not self._active:
            return
        if self._audio is not None:
            self._audio.feed(data)

    def _begin_preroll(self, keyframe):
        """Prime Qt's FFmpeg probe with keyframes so it loads instantly.

        Qt's FFmpeg loader waits for about 2.5 s of media before it reports
        LoadedMedia.  On a live source that delay lands playback in the
        middle of a GOP (choppy until the next keyframe).  Feeding copies of
        the current I-frame satisfies the probe immediately; the real frames
        are held until the loader is done, then replayed from the keyframe.
        """
        self._preroll_timer.stop()
        self._preroll_feed_timer.stop()
        self._preroll_active = False
        self._preroll_frames = []
        self._preroll_keyframe = bytes(keyframe or b"")
        device = self._stream_device
        if device is None or not self._preroll_keyframe:
            return
        self._preroll_active = True
        for _ in range(32):
            device.feed(self._preroll_keyframe)
        self._preroll_feed_timer.start()
        self._preroll_timer.start(4000)

    def _feed_preroll(self):
        if not self._preroll_active:
            self._preroll_feed_timer.stop()
            return
        device = self._stream_device
        if device is None:
            self._flush_preroll()
            return
        for _ in range(6):
            device.feed(self._preroll_keyframe)

    def _on_qt_media_status(self, status):
        if not self._preroll_active:
            return
        if status in (QMediaPlayer.MediaStatus.LoadedMedia,
                      QMediaPlayer.MediaStatus.BufferingMedia,
                      QMediaPlayer.MediaStatus.BufferedMedia):
            self._flush_preroll()

    def _flush_preroll(self):
        if not self._preroll_active:
            return
        self._preroll_active = False
        self._preroll_timer.stop()
        self._preroll_feed_timer.stop()
        device = self._stream_device
        frames = self._preroll_frames
        self._preroll_frames = []
        if device is None:
            return
        device.clear()
        for data in frames:
            device.feed(data)

    def _restart_qt_source(self):
        if self._player is None:
            return
        old_device = self._stream_device
        if old_device is not None:
            old_device.end()
            self._retired_devices.append(old_device)
            self._stream_device = None
        self._player.setSource(QUrl())
        device = LiveStreamDevice(self)
        device.open(QIODevice.OpenModeFlag.ReadOnly)
        self._stream_device = device
        suffix = {"h264": "h264", "h265": "h265", "mpeg4": "m4v",
                  "jpeg": "mjpeg"}.get(self._qt_codec or "", "bin")
        self._player.setSourceDevice(device, QUrl("stream." + suffix))
        self._player.play()
        if self.video_view is not None:
            self._stack.setCurrentWidget(self.video_view)

    def _on_video_frame(self, frame):
        if frame.isValid():
            self._frame_size = (frame.width(), frame.height())
            if self.focus_button.isChecked() and self._active:
                now = time.monotonic()
                if now - self._focus_last >= FOCUS_INTERVAL:
                    self._focus_last = now
                    image = frame.toImage()
                    if not image.isNull():
                        self._focus_analyze(image)

    def _on_qt_error(self, error, text):
        if not self._active:
            return
        message = text or str(error)
        if self._decoded == 0 and not self._fallback_started:
            self._start_fallback("Qt video failed (%s)" % message)
        else:
            self._set_status("Video error: %s" % message)

    def _watchdog_fired(self):
        if self._decoded > 0 or self._thread is None or self._backend != "qt":
            return
        self._start_fallback("No Qt video after 6s")

    def _start_fallback(self, reason):
        if not self._active or self._backend != "qt" or self._fallback_started:
            return
        self._fallback_started = True
        self._backend = "av" if self._av_decoder is not None else "ffmpeg"
        self._set_status("%s — using %s decoder" % (reason, self._backend))
        if self._device is not None:
            self.stop()
            self._start_thread()

    def _show_image(self, image):
        self._image = image
        self._frame_size = (image.width(), image.height())
        if self._stack.currentWidget() is not self.video_label:
            self._stack.setCurrentWidget(self.video_label)
        self._update_pixmap()
        self._focus_maybe_update(image)

    def _on_image(self, image):
        if isinstance(image, QImage) and not image.isNull():
            self._show_image(image)

    def _on_decoder_failed(self, text):
        if not self._active:
            return
        self._set_status("Error: %s" % text)

    def _set_status(self, text):
        self.status_changed.emit(text)

    def _toggle_focus(self, checked):
        if checked and not self._active:
            self.focus_button.blockSignals(True)
            self.focus_button.setChecked(False)
            self.focus_button.blockSignals(False)
            return
        if not checked:
            self.focus_overlay.hide()
            return
        self._focus_last = 0.0
        self.focus_overlay.set_frame_size(self._frame_size)
        self.focus_overlay.clear()
        self._position_focus_overlay()
        self.focus_overlay.show()
        self.focus_overlay.raise_()
        if self._image is not None:
            self._focus_analyze(self._image)

    def _focus_analyze(self, image):
        scores, overall, low_detail = analyze_focus(image)
        self.focus_overlay.set_frame_size((image.width(), image.height()))
        self.focus_overlay.set_scores(scores, overall, low_detail)
        self._position_focus_overlay()

    def _focus_maybe_update(self, image):
        if not self.focus_button.isChecked() or not self._active:
            return
        now = time.monotonic()
        if now - self._focus_last < FOCUS_INTERVAL:
            return
        self._focus_last = now
        self._focus_analyze(image)

    def _position_focus_overlay(self):
        if not hasattr(self, "focus_overlay"):
            return
        self.focus_overlay.setGeometry(self._stack.geometry())
        if self.focus_button.isChecked():
            self.focus_overlay.raise_()

    def _reset_focus(self):
        self.focus_button.blockSignals(True)
        self.focus_button.setChecked(False)
        self.focus_button.blockSignals(False)
        self.focus_button.setEnabled(False)
        self.focus_overlay.hide()
        self.focus_overlay.clear()

    def is_active(self):
        return self._thread is not None

    def start(self, device, username, password, stream="Main", channel=0):
        self.stop()
        self._device = device
        self._username = username
        self._password = password
        self._stream = stream
        self._channel = int(channel)
        self._fallback_started = False
        self._backend = self._choose_backend()
        return self._start_thread()

    def _start_thread(self):
        if not self.available():
            self._set_status("No video decoder available.")
            return False
        self._source_dirty = True
        self._qt_codec = None
        self.codec = None
        self._decoded = 0
        self._preroll_active = False
        self._preroll_frames = []
        self._preroll_keyframe = b""
        self._preroll_timer.stop()
        self._preroll_feed_timer.stop()
        self._image = None
        self._frame_size = None
        self._last_frame_time = 0.0
        self._stack.setCurrentWidget(self.video_label)
        self.video_label.setText("waiting for video ...")
        self.video_label.setPixmap(QPixmap())
        self._media_generation += 1
        self._decoder.reset()
        if self._av_decoder is not None:
            self._av_decoder.reset()
        thread = NetipVideoThread(
            self._device.get("ip") or "", self._username, self._password, self,
            cloud_id=self._device.get("cloud_id") or "",
            rps=bool(self._device.get("rps", True)),
            port=int(self._device.get("tcp_port") or 34567),
            stream=self._stream, channel=self._channel, parent=self,
            audio_sink=self,
            no_md5=bool(self._device.get("no_md5")))
        thread.status.connect(self._set_status)
        thread.stats.connect(self._on_stats)
        thread.failed.connect(self._on_failed)
        thread.keyframe.connect(self._on_keyframe)
        thread.finished.connect(self._on_finished)
        self._thread = thread
        self._active = True
        self._watchdog.start(6000)
        thread.start()
        self.focus_button.setEnabled(True)
        return True

    def _on_keyframe(self):
        self._switch_target = None
        self._switch_timer.stop()
        self.keyframe.emit()

    def switch(self, stream, channel):
        if self._thread is None:
            return False
        if self._recorder.is_recording:
            self._uncheck_record()
            self._stop_recording()
            self.notice.emit("Recording stopped for the channel switch")
        self._stream = stream
        self._channel = int(channel)
        self._switch_target = (stream, int(channel))
        self._switch_mark = self._decoded
        self._focus_last = 0.0
        if self.focus_button.isChecked():
            self.focus_overlay.clear()
        self._switch_deadline = time.monotonic() + 2.0
        self._thread.switch(stream, channel)
        self._switch_timer.start()
        return True

    def _check_switch(self):
        if self._switch_target is None:
            self._switch_timer.stop()
            return
        if self._decoded > self._switch_mark:
            self._switch_target = None
            self._switch_timer.stop()
            return
        if time.monotonic() >= self._switch_deadline:
            self._switch_target = None
            self._switch_timer.stop()

    def stop(self, wait=False):
        self._active = False
        self._reset_focus()
        self._watchdog.stop()
        self._switch_timer.stop()
        self._switch_target = None
        self._uncheck_record()
        self._stop_recording()
        # Hide the frame immediately and repaint now; the device/player
        # cleanup runs afterwards and must never delay the visible change.
        self._image = None
        self._frame_size = None
        self.video_label.setPixmap(QPixmap())
        self.video_label.setText("no video")
        self._stack.setCurrentWidget(self.video_label)
        self._stack.repaint()
        self._set_status("")
        thread = self._thread
        self._thread = None
        if thread is not None:
            thread.stop()
            if wait:
                thread.wait(3000)
            thread.finished.connect(thread.deleteLater)
        self._media_generation += 1
        if wait:
            self._stop_media(self._media_generation)
        else:
            generation = self._media_generation
            QTimer.singleShot(0, lambda: self._stop_media(generation))

    def _stop_media(self, generation):
        if generation != self._media_generation:
            return
        self._preroll_active = False
        self._preroll_frames = []
        self._preroll_timer.stop()
        self._preroll_feed_timer.stop()
        if self._stream_device is not None:
            self._stream_device.end()
            self._stream_device = None
        if self._player is not None:
            self._player.stop()
            self._player.setSource(QUrl())
        self._decoder.stop()
        if self._av_decoder is not None:
            self._av_decoder.stop()
        if self._audio is not None:
            self._audio.stop()

    def _on_frame(self, generation, data):
        if generation != self._decoder.generation:
            return
        self._last_frame_time = time.monotonic()
        image = QImage.fromData(data, "JPG")
        if image.isNull():
            return
        self._show_image(image)

    def _update_pixmap(self):
        if self._image is None or self._stack.currentWidget() is not self.video_label:
            return
        pixmap = QPixmap.fromImage(self._image)
        self.video_label.setPixmap(pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation))

    def resizeEvent(self, event):
        self._update_pixmap()
        self._position_focus_overlay()
        super().resizeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._position_focus_overlay)

    def _on_stats(self, text):
        if self._frame_size is not None:
            resolution = "%dx%d" % self._frame_size
        elif self._image is not None:
            resolution = "%dx%d" % (self._image.width(), self._image.height())
        else:
            resolution = "?x?"
        self._set_status("%s channel %d — %s  %s" % (
            self._stream, self._channel + 1, resolution, text))

    def _on_failed(self, text):
        if not self._active:
            return
        self._set_status("Error: %s" % text)
        if is_connection_error(text):
            self.lost.emit(str(text))

    def _on_finished(self):
        thread = self.sender()
        if thread is self._thread:
            self._thread = None
        if thread is not None:
            thread.deleteLater()

    def _toggle_recording(self, checked):
        if not checked:
            self._stop_recording()
            return
        if not self._active:
            self._uncheck_record()
            return
        codec = self._qt_codec or self.codec or ""
        suffix = {"h264": ".h264", "h265": ".h265", "mpeg4": ".m4v",
                  "jpeg": ".mjpeg"}.get(codec, ".bin")
        settings = QSettings("xmdm3", "xmdms")
        start_dir = str(settings.value("video_dir", "", type=str) or "")
        device = self._device if isinstance(self._device, dict) else {}
        base = "%s_%s" % ((device.get("ip") or "stream").replace(".", "-"),
                          time.strftime("%Y%m%d-%H%M%S"))
        path, _ = QFileDialog.getSaveFileName(
            self, "Save stream", os.path.join(start_dir, base + suffix),
            "Video stream (*%s);;All files (*)" % suffix)
        if not path:
            self._uncheck_record()
            return
        settings.setValue("video_dir", os.path.dirname(path))
        error = self._recorder.start(path, wait_keyframe=(codec != "jpeg"))
        if error is not None:
            self._uncheck_record()
            self.notice.emit("Cannot save stream: %s" % error)
            return
        self.record_label.setText("REC")
        self.notice.emit("Saving stream to %s" % path)

    def _stop_recording(self):
        result = self._recorder.stop()
        self.record_label.setText("")
        if result is None:
            return
        path, size = result
        if size >= 1048576:
            text = "%.1f MB" % (size / 1048576.0)
        elif size >= 1024:
            text = "%.1f KB" % (size / 1024.0)
        else:
            text = "%d B" % size
        self.notice.emit("Stream saved: %s (%s)" % (path, text))

    def _uncheck_record(self):
        self.record_button.blockSignals(True)
        self.record_button.setChecked(False)
        self.record_button.blockSignals(False)

    def _on_mute(self, checked):
        if self._audio is not None:
            self._audio.set_muted(checked)

    def _on_volume(self, value):
        if self._audio is not None:
            self._audio.set_volume(value / 100.0)


class QueryConsoleDialog(QDialog):
    def __init__(self, bus, parent=None):
        super().__init__(parent)
        self._bus = bus
        self.setWindowTitle("Query console")
        self.resize(920, 620)

        self.fold_spin = QSpinBox()
        self.fold_spin.setRange(1, 32)
        self.fold_spin.setValue(3)
        self.fold_spin.setSuffix(" levels")
        self.fold_spin.valueChanged.connect(self._apply_fold)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self._clear)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Fold deeper than:"))
        bar.addWidget(self.fold_spin)
        bar.addStretch(1)
        bar.addWidget(clear_button)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(("Field", "Value"))
        self.tree.header().setStretchLastSection(True)
        self.tree.setColumnWidth(0, 320)
        self.tree.setAlternatingRowColors(True)

        layout = QVBoxLayout(self)
        layout.addLayout(bar)
        layout.addWidget(self.tree, 1)

        for header, payload in bus.history:
            self._append(header, payload)
        bus.record.connect(self._append)

    def _clear(self):
        self.tree.clear()

    def _append(self, header, payload):
        root = QTreeWidgetItem([header, ""])
        self._fill(root, payload, 1)
        self.tree.addTopLevelItem(root)
        self._fold_item(root, 0)
        while self.tree.topLevelItemCount() > 500:
            self.tree.takeTopLevelItem(0)
        self.tree.scrollToItem(root)

    def _fill(self, parent, value, depth):
        if isinstance(value, dict):
            for key, child in value.items():
                self._add_node(parent, key, child, depth)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                self._add_node(parent, index, child, depth)
        else:
            parent.setText(1, self._scalar(value))

    def _add_node(self, parent, key, value, depth):
        item = QTreeWidgetItem([self._text(key), ""])
        parent.addChild(item)
        if isinstance(value, dict):
            item.setText(1, "{ %d }" % len(value))
            self._fill(item, value, depth + 1)
        elif isinstance(value, list):
            item.setText(1, "[ %d ]" % len(value))
            self._fill(item, value, depth + 1)
        else:
            item.setText(1, self._scalar(value))

    @staticmethod
    def _text(value):
        return "" if value is None else str(value)

    @staticmethod
    def _scalar(value):
        if value is None:
            return "null"
        if value is True:
            return "true"
        if value is False:
            return "false"
        return str(value)

    def _fold_item(self, item, depth):
        item.setExpanded(depth <= self.fold_spin.value())
        for index in range(item.childCount()):
            self._fold_item(item.child(index), depth + 1)

    def _apply_fold(self):
        for index in range(self.tree.topLevelItemCount()):
            self._fold_item(self.tree.topLevelItem(index), 0)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("XiongMai DMS")
        self.setWindowIcon(app_icon())
        self.resize(1280, 560)
        self._thread = None
        self._ipset_thread = None
        self._session_thread = None
        self._ipset_target = None
        self._search_seen = set()
        self._search_devices = {}
        self._search_error = False
        self._pass_thread = None
        self._pass_queue = []
        self._pass_active = False
        self._pass_total = 0
        self._pass_done = 0
        self._pass_failed = 0
        self._probe_thread = None
        self._release_thread = None
        self._updates_checked = False
        self._about_state = ("idle", None)
        self._netip_thread = None
        self._network_thread = None
        self._pending_network = None
        self._network_dhcp_config = []
        self._channels_dialog = None
        self._snapshot_windows = []
        self._console_dialog = None
        self._video_device = None
        self._video_credentials = ("admin", "")
        self._system_payload = None
        self._fetched_payload = None
        self._fetched_identity = None
        self._fetched_keys = set()
        self._pending_fetch_keys = set()
        self._fetch_in_progress = False
        self._system_error = False
        self._channel_count = 0
        self._stale_threads = []
        self._connect_pending = None
        self._connected_identity = None
        self._age_build_time = None
        self._age_runtime = None
        self._age_timer = QTimer(self)
        self._age_timer.setInterval(60000)
        self._age_timer.timeout.connect(self._refresh_age_label)
        self._age_timer.start()
        self._paused = False
        self._status_text = "Idle"
        self._idle_text = "Stopped"
        self._number_queue = []
        self._number_active = False
        self._number_total = 0
        self._number_done = 0
        self._number_failed = 0
        self._number_attempts = {}
        self._number_device_map = {}
        self._number_interface = {}

        self.model = DeviceTableModel(self)
        self._interfaces = list_interfaces()

        self.user_edit = QLineEdit("admin")
        self.user_edit.setMaximumWidth(110)
        self.password_edit = QLineEdit()
        configure_password_edit(self.password_edit)
        self.password_edit.setMaximumWidth(100)
        self.new_password_edit = QLineEdit()
        configure_password_edit(self.new_password_edit)
        self.new_password_edit.setMaximumWidth(100)

        self.initial_ip_edit = IpAddressEdit()
        self.initial_ip_edit.setValue("0.0.0.0")
        self.initial_ip_edit.setToolTip(
            "First IP to assign. Set automatically to the selected device IP + 1; "
            "can be edited manually.")
        self.number_button = QPushButton("Provision")
        self.number_button.clicked.connect(self._number_devices)

        self.interface_combo = QComboBox()
        for interface in self._interfaces:
            label = "%s (%s)" % (interface["name"], interface["ip"]) if interface["ip"] else interface["name"]
            self.interface_combo.addItem(label, interface)
        default_index = 0
        for index, interface in enumerate(self._interfaces):
            if interface.get("default"):
                default_index = index
                break
        self.interface_combo.setCurrentIndex(default_index)

        self.search_button = QPushButton("Search")
        self.search_button.setCheckable(True)
        self.search_button.toggled.connect(self._toggle_search)

        self.status_label = QLabel(self._refresh_status_text())
        self.status_label.setProperty("i18nDynamic", True)
        self.status_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("User:"))
        controls.addWidget(self.user_edit)
        controls.addWidget(QLabel("Password:"))
        controls.addWidget(self.password_edit)
        controls.addWidget(QLabel("New password:"))
        controls.addWidget(self.new_password_edit)
        self.change_button = QPushButton("Change")
        self.change_button.setToolTip(
            "Change the password on all checked devices (or the selected one).")
        self.change_button.clicked.connect(self._change_passwords)
        controls.addWidget(self.change_button)
        controls.addWidget(QLabel("Start IP:"))
        controls.addWidget(self.initial_ip_edit)
        controls.addWidget(self.number_button)
        controls.addWidget(QLabel("Interface:"))
        controls.addWidget(self.interface_combo, 1)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(2, Qt.SortOrder.AscendingOrder)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.header = CheckableHeaderView(self.table)
        self.table.setHorizontalHeader(self.header)
        self.table.sortByColumn(2, Qt.SortOrder.AscendingOrder)
        self.header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.header.setStretchLastSection(True)
        self.header.toggled.connect(self.model.set_all_checked)
        self.model.check_state_changed.connect(self.header.set_check_state)
        metrics = self.table.fontMetrics()
        indicator = self.style().pixelMetric(QStyle.PixelMetric.PM_IndicatorWidth)
        self.header.setMinimumSectionSize(indicator + 10)
        self.table.setColumnWidth(0, indicator + 10)
        measurements = (
            "999",
            "255.255.255.255",
            "FF:FF:FF:FF:FF:FF",
            "F" * 20,
            "V5.00.R02.00030695",
            "0000-00-00 00:00:00",
        )
        for column, sample in enumerate(measurements, start=1):
            self.table.setColumnWidth(column, metrics.horizontalAdvance(sample) + 16)
        self.table.selectionModel().selectionChanged.connect(self._on_table_selection)
        self.model.layoutChanged.connect(self._on_model_layout_changed)
        self.table.doubleClicked.connect(self._connect_device)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._table_context_menu)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self._add_device)
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self._export_devices)
        self.rtsp_button = QPushButton("RTSP")
        self.rtsp_button.clicked.connect(self._copy_rtsp)
        self.snap_button = QPushButton("SNAP")
        self.snap_button.clicked.connect(self._open_snapshot)
        self.video_button = QPushButton("START VIDEO")
        self.video_button.clicked.connect(self._toggle_video)

        self.stream_main_radio = QRadioButton("Main")
        self.stream_sub_radio = QRadioButton("Sub")
        self.stream_main_radio.setChecked(True)
        self.channel_combo = QComboBox()
        self._set_channel_count(16)
        self.channel_combo.currentIndexChanged.connect(self._video_source_changed)
        self.stream_main_radio.toggled.connect(self._stream_radio_changed)
        self.stream_sub_radio.toggled.connect(self._stream_radio_changed)

        bottom = QHBoxLayout()
        bottom.addWidget(self.search_button)
        bottom.addWidget(self.add_button)
        bottom.addWidget(self.export_button)
        bottom.addWidget(self.rtsp_button)
        bottom.addWidget(self.snap_button)
        bottom.addWidget(self.video_button)
        bottom.addWidget(QLabel("Channel:"))
        bottom.addWidget(self.channel_combo)
        bottom.addWidget(QLabel("Stream:"))
        bottom.addWidget(self.stream_main_radio)
        bottom.addWidget(self.stream_sub_radio)
        bottom.addStretch(1)

        self.video_panel = VideoPanel()
        self.table_stack = QStackedWidget()
        self.table_stack.addWidget(self.table)
        self.table_stack.addWidget(self.video_panel)

        table_panel = QWidget()
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.addWidget(self.table_stack, 1)
        table_layout.addLayout(bottom)

        self.network_name_edit = QLineEdit()
        self.network_address_edit = IpAddressEdit()
        self.network_submask_edit = IpAddressEdit()
        self.network_gateway_edit = IpAddressEdit()
        self.network_dns1_edit = IpAddressEdit()
        self.network_dns2_edit = IpAddressEdit()
        self.network_default_ip_button = QPushButton("Default IP")
        self.network_default_ip_button.clicked.connect(
            lambda: self.network_address_edit.setValue("192.168.1.10"))
        self.network_default_dns_button = QPushButton("Default DNS")
        self.network_default_dns_button.clicked.connect(self._set_default_dns)
        self.network_adaptive_check = QCheckBox("IP adaptive")
        self.network_dhcp_check = QCheckBox("DHCP")
        self.network_smartnet_check = QCheckBox("SmartNet")
        self.network_smartnet_auto_check = QCheckBox("Auto connect")
        self.network_smartnet_change_ip_check = QCheckBox("Change IP")
        self.network_upnp_check = QCheckBox("UPnP")
        self.network_onvif_pwd_check = QCheckBox("OnvifPwdCheckout")
        self.network_pms_check = QCheckBox("PMS")
        self.network_force_dhcp_check = QCheckBox("ForceNetDHCP")
        self.network_hsdownload_check = QCheckBox("UseHSDownLoad")
        self.network_vnic_check = QCheckBox("VNIC")
        self._network_ability_config = {}
        self.network_transfer_combo = QComboBox()
        self.network_transfer_combo.setEditable(True)
        self.network_transfer_combo.addItems(
            ["Quality", "Fluency", "Transmission", "AutoAdapt"])
        self._network_disable_conn_config = {}
        self._network_oemcfg_config = {}
        self.network_disable_conn_container = QWidget()
        self.network_disable_conn_layout = QHBoxLayout(self.network_disable_conn_container)
        self.network_disable_conn_layout.setContentsMargins(0, 0, 0, 0)
        self.network_disable_conn_layout.setSpacing(6)
        self._disable_conn_checks = {}
        self.network_disable_conn_layout.addStretch(1)
        for key in ("DisableAll", "DisableDSS", "DisableNAT", "DisableRPS"):
            check = QCheckBox(key)
            check.setEnabled(False)
            self.network_disable_conn_layout.addWidget(check)
            self._disable_conn_checks[key] = check
        self.network_disable_conn_layout.addStretch(1)
        self.network_nat_addr_edit = QLineEdit()
        self.network_nat_dns1_edit = IpAddressEdit()
        self.network_nat_dns2_edit = IpAddressEdit()
        self.network_nat_port_edit = build_port_edit(8000)
        self.network_nat_port_edit.setMaximumWidth(60)
        self.network_nat_mtu_edit = build_port_edit(1280)
        self.network_nat_mtu_edit.setMaximumWidth(60)
        self._network_nat_config = {}
        self.network_ntp_auto_radio = QRadioButton("Auto")
        self.network_ntp_manual_radio = QRadioButton("Manual")
        self.network_ntp_server_edit = QLineEdit()
        self.network_ntp_server_edit.setEnabled(False)
        self.network_ntp_manual_radio.toggled.connect(self.network_ntp_server_edit.setEnabled)
        self.network_ntp_default_button = QPushButton("Default")
        self.network_ntp_default_button.clicked.connect(
            lambda: self.network_ntp_server_edit.setText("ru.pool.ntp.org"))
        self.network_ntp_period_edit = QLineEdit("60")
        self.network_ntp_period_edit.setValidator(
            QIntValidator(0, 999, self.network_ntp_period_edit))
        self.network_ntp_period_edit.setMaximumWidth(46)
        self.network_pubcfg_edit = QLineEdit()
        self.network_caps_edit = QLineEdit()
        self._network_upnp_config = {}
        self._network_onvif_pwd_config = {}
        self._network_pms_config = {}
        self._network_ntp_config = {}
        self.network_wifi_ssid_edit = QComboBox()
        self.network_wifi_ssid_edit.setEditable(True)
        self.network_wifi_ssid_edit.activated.connect(
            self._wifi_ssid_activated)
        self.network_wifi_scan_button = QPushButton("Scan")
        self.network_wifi_scan_button.setToolTip(
            "Scan for Wi-Fi networks on the device.")
        self.network_wifi_scan_button.clicked.connect(self._wifi_scan)
        self.network_wifi_password_edit = QLineEdit()
        configure_password_edit(self.network_wifi_password_edit)
        self.network_wifi_auth_combo = QComboBox()
        self.network_wifi_auth_combo.addItems(
            ["OPEN", "SHARED", "WEPAUTO", "WPAPSK", "WPA2PSK", "WPANONE", "WPA", "WPA2"])
        self.network_wifi_encrypt_combo = QComboBox()
        self.network_wifi_encrypt_combo.addItems(["NONE", "WEP", "TKIP", "AES"])
        self.network_wifi_nettype_combo = QComboBox()
        self.network_wifi_nettype_combo.addItems(["Infra", "Adhoc"])
        self._network_wifi_config = {}
        self._network_rtsp_config = {}
        self.network_upgrade_server_edit = QLineEdit()
        self.network_upgrade_server_edit.setMaximumWidth(150)
        self.network_upgrade_button = QPushButton("Upgrade")
        self.network_upgrade_button.clicked.connect(self._upgrade_firmware)
        self.network_cloud_upgrade_button = QPushButton("Cloud upgrade")
        self.network_cloud_upgrade_button.clicked.connect(self._cloud_upgrade)
        self.network_upgrade_file_edit = QLineEdit()
        self.network_upgrade_file_edit.setReadOnly(True)
        self.network_upgrade_file_edit.setPlaceholderText("firmware...")
        pick_action = self.network_upgrade_file_edit.addAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon),
            QLineEdit.ActionPosition.TrailingPosition)
        pick_action.triggered.connect(self._browse_firmware)
        self.network_upgrade_port_edit = build_port_edit(8083)
        self.network_upgrade_autocheck_check = QCheckBox("Auto check")
        self.network_upgrade_autoimp_check = QCheckBox("Auto upgrade")
        self.network_upgrade_ignore_all_check = QCheckBox("Ignore all ver")
        self.network_upgrade_ignore_all_check.setToolTip("IgnoreAllVersion")
        self.network_upgrade_ignore_time_check = QCheckBox("Ignore cur time")
        self.network_upgrade_ignore_time_check.setToolTip("IgnoreCurTime")
        self.network_upgrade_ignore_version_check = QCheckBox("Ignore cur ver")
        self.network_upgrade_ignore_version_check.setToolTip("IgnoreCurVersion")
        self.network_upgrade_just_imp_check = QCheckBox("Just imp ver")
        self.network_upgrade_just_imp_check.setToolTip("JustImpVersion")
        self._network_upgrade_config = {}
        self.network_http_edit = build_port_edit(80)
        self.network_tcp_edit = build_port_edit(34567)
        self.network_rtsp_edit = build_port_edit(554)
        self.network_onvif_edit = build_port_edit(8899)
        self.network_dns1_edit.setEnabled(False)
        self.network_dns2_edit.setEnabled(False)
        self.network_default_dns_button.setEnabled(False)
        self.network_adaptive_check.setEnabled(False)
        self.network_dhcp_check.setEnabled(False)
        self.network_smartnet_check.setEnabled(False)
        self.network_smartnet_auto_check.setEnabled(False)
        self.network_smartnet_change_ip_check.setEnabled(False)

        lan_group = QGroupBox("LAN")
        lan_group.setStyleSheet(GROUP_BOX_STYLE)
        form = QGridLayout(lan_group)
        form.setVerticalSpacing(3)
        form.setColumnStretch(1, 1)
        form.addWidget(QLabel("Name:"), 0, 0)
        form.addWidget(self.network_name_edit, 0, 1)
        form.addWidget(self.network_transfer_combo, 0, 2)
        form.addWidget(QLabel("IP:"), 1, 0)
        form.addWidget(self.network_address_edit, 1, 1)
        form.addWidget(self.network_default_ip_button, 1, 2)
        form.addWidget(QLabel("Subnet:"), 2, 0)
        form.addWidget(self.network_submask_edit, 2, 1)
        form.addWidget(QLabel("Gateway:"), 3, 0)
        form.addWidget(self.network_gateway_edit, 3, 1)
        form.setRowMinimumHeight(4, 6)
        form.addWidget(QLabel("DNS 1:"), 5, 0)
        form.addWidget(self.network_dns1_edit, 5, 1)
        form.addWidget(QLabel("DNS 2:"), 6, 0)
        form.addWidget(self.network_dns2_edit, 6, 1)
        form.addWidget(self.network_default_dns_button, 6, 2)
        form.setRowMinimumHeight(7, 6)
        checkbox_grid = QGridLayout()
        checkbox_grid.setHorizontalSpacing(6)
        checkbox_grid.setVerticalSpacing(3)
        checkbox_grid.addWidget(self.network_dhcp_check, 0, 0)
        checkbox_grid.addWidget(self.network_upnp_check, 0, 1)
        checkbox_grid.addWidget(self.network_smartnet_check, 0, 2)
        checkbox_grid.addWidget(self.network_force_dhcp_check, 1, 0)
        checkbox_grid.addWidget(self.network_pms_check, 1, 1)
        checkbox_grid.addWidget(self.network_smartnet_change_ip_check, 1, 2)
        checkbox_grid.addWidget(self.network_adaptive_check, 2, 0)
        checkbox_grid.addWidget(self.network_onvif_pwd_check, 2, 1)
        checkbox_grid.addWidget(self.network_smartnet_auto_check, 2, 2)
        checkbox_grid.addWidget(self.network_vnic_check, 3, 0)
        checkbox_grid.addWidget(self.network_hsdownload_check, 3, 1)
        form.addLayout(checkbox_grid, 8, 0, 4, 3)

        ports = QVBoxLayout()
        ports.setSpacing(2)
        ports.addWidget(QLabel("HTTP"))
        ports.addWidget(self.network_http_edit)
        ports.addWidget(QLabel("TCP"))
        ports.addWidget(self.network_tcp_edit)
        ports.addWidget(QLabel("RTSP"))
        ports.addWidget(self.network_rtsp_edit)
        ports.addWidget(QLabel("ONVIF"))
        ports.addWidget(self.network_onvif_edit)
        ports.addStretch(1)

        wifi_group = QGroupBox("Wi-Fi")
        wifi_group.setCheckable(True)
        wifi_group.setStyleSheet(GROUP_BOX_STYLE)
        self.wifi_group = wifi_group
        wifi_grid = QGridLayout(wifi_group)
        wifi_grid.setHorizontalSpacing(6)
        wifi_grid.setVerticalSpacing(3)
        wifi_grid.addWidget(QLabel("SSID:"), 1, 0)
        ssid_row = QHBoxLayout()
        ssid_row.setContentsMargins(0, 0, 0, 0)
        ssid_row.setSpacing(4)
        ssid_row.addWidget(self.network_wifi_ssid_edit, 1)
        ssid_row.addWidget(self.network_wifi_scan_button)
        wifi_grid.addLayout(ssid_row, 1, 1)
        wifi_grid.addWidget(QLabel("Pass:"), 2, 0)
        wifi_grid.addWidget(self.network_wifi_password_edit, 2, 1)
        wifi_modes = QHBoxLayout()
        wifi_modes.setSpacing(4)
        wifi_modes.addWidget(QLabel("Sec:"))
        wifi_modes.addWidget(self.network_wifi_auth_combo, 1)
        wifi_modes.addWidget(QLabel("Enc:"))
        wifi_modes.addWidget(self.network_wifi_encrypt_combo, 1)
        wifi_modes.addWidget(QLabel("Net:"))
        wifi_modes.addWidget(self.network_wifi_nettype_combo, 1)
        wifi_grid.addLayout(wifi_modes, 3, 0, 1, 2)
        wifi_grid.setColumnStretch(1, 1)

        upgrade_group = QGroupBox("Upgrade")
        upgrade_group.setCheckable(True)
        upgrade_group.setStyleSheet(GROUP_BOX_STYLE)
        upgrade_group.toggled.connect(self._update_upgrade_controls)
        self.upgrade_group = upgrade_group
        upgrade_grid = QGridLayout(upgrade_group)
        upgrade_grid.setHorizontalSpacing(6)
        upgrade_grid.setVerticalSpacing(3)
        upgrade_grid.addWidget(QLabel("Server:"), 1, 0)
        upgrade_grid.addWidget(self.network_upgrade_server_edit, 1, 1, 1, 2)
        upgrade_grid.addWidget(QLabel("Port:"), 1, 3)
        upgrade_grid.addWidget(self.network_upgrade_port_edit, 1, 4)
        upgrade_grid.addWidget(self.network_cloud_upgrade_button, 1, 5)
        upgrade_grid.addWidget(self.network_upgrade_file_edit, 2, 0, 1, 5)
        upgrade_grid.addWidget(self.network_upgrade_button, 2, 5)
        upgrade_grid.addWidget(self.network_upgrade_autocheck_check, 3, 0, 1, 2)
        upgrade_grid.addWidget(self.network_upgrade_autoimp_check, 3, 2, 1, 2)
        upgrade_grid.addWidget(self.network_upgrade_ignore_all_check, 3, 4, 1, 2)
        upgrade_grid.addWidget(self.network_upgrade_ignore_time_check, 4, 0, 1, 2)
        upgrade_grid.addWidget(self.network_upgrade_ignore_version_check, 4, 2, 1, 2)
        upgrade_grid.addWidget(self.network_upgrade_just_imp_check, 4, 4, 1, 2)
        upgrade_grid.setColumnStretch(1, 1)

        nat_group = QGroupBox("Nat")
        nat_group.setCheckable(True)
        nat_group.setStyleSheet(GROUP_BOX_STYLE)
        self.nat_group = nat_group
        nat_grid = QGridLayout(nat_group)
        nat_grid.setHorizontalSpacing(6)
        nat_grid.setVerticalSpacing(3)
        nat_grid.setColumnMinimumWidth(
            0, self.fontMetrics().horizontalAdvance("PubCfg:"))
        nat_grid.addWidget(QLabel("Addr:"), 0, 0)
        nat_grid.addWidget(self.network_nat_addr_edit, 0, 1, 1, 4)
        nat_grid.addWidget(QLabel("DNS 1:"), 1, 0)
        nat_grid.addWidget(self.network_nat_dns1_edit, 1, 1, 1, 2)
        nat_grid.addWidget(QLabel("Port:"), 1, 3)
        nat_grid.addWidget(self.network_nat_port_edit, 1, 4)
        nat_grid.addWidget(QLabel("DNS 2:"), 2, 0)
        nat_grid.addWidget(self.network_nat_dns2_edit, 2, 1, 1, 2)
        nat_grid.addWidget(QLabel("MTU:"), 2, 3)
        nat_grid.addWidget(self.network_nat_mtu_edit, 2, 4)
        domains_row = QHBoxLayout()
        domains_row.setSpacing(6)
        domains_row.addWidget(QLabel("PubCfg:"))
        domains_row.addWidget(self.network_pubcfg_edit, 1)
        domains_row.addWidget(QLabel("Caps:"))
        domains_row.addWidget(self.network_caps_edit, 1)
        nat_grid.addLayout(domains_row, 3, 0, 1, 5)
        nat_grid.addWidget(self.network_disable_conn_container, 4, 0, 1, 5)
        nat_grid.setColumnStretch(1, 1)
        nat_grid.setColumnStretch(4, 1)
        nat_grid.setColumnStretch(3, 1)

        ntp_group = QGroupBox("NTP")
        ntp_group.setCheckable(True)
        ntp_group.setStyleSheet(GROUP_BOX_STYLE)
        self.ntp_group = ntp_group
        ntp_grid = QGridLayout(ntp_group)
        ntp_grid.setHorizontalSpacing(6)
        ntp_grid.setVerticalSpacing(3)
        ntp_row = QHBoxLayout()
        ntp_row.setSpacing(6)
        ntp_row.addWidget(QLabel("Period:"))
        ntp_row.addWidget(self.network_ntp_period_edit)
        ntp_row.addWidget(self.network_ntp_auto_radio)
        ntp_row.addWidget(self.network_ntp_manual_radio)
        ntp_row.addWidget(self.network_ntp_server_edit, 1)
        ntp_row.addWidget(self.network_ntp_default_button)
        ntp_grid.addLayout(ntp_row, 0, 0, 1, 2)
        ntp_grid.setColumnStretch(0, 1)

        lan_row = QHBoxLayout()
        lan_row.addWidget(lan_group, 1)
        lan_row.addLayout(ports)

        network_panel = QWidget()
        network_layout = QVBoxLayout(network_panel)
        network_layout.addLayout(lan_row)
        network_layout.addWidget(nat_group)
        network_layout.addWidget(ntp_group)
        network_layout.addWidget(upgrade_group)
        network_layout.addWidget(wifi_group)
        network_layout.addStretch(1)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.East)
        self.tabs.addTab(network_panel, "Network")

        self.settings_timeout_spin = QSpinBox()
        self.settings_timeout_spin.setRange(1, 600)
        self.settings_timeout_spin.setSuffix(" s")
        saved_timeout = QSettings("xmdm3", "xmdms").value(
            "search_timeout", 5, type=int)
        self.settings_timeout_spin.setValue(
            min(max(int(saved_timeout or 5), 1), 600))
        self.settings_attempts_spin = QSpinBox()
        self.settings_attempts_spin.setRange(3, 100)
        saved_attempts = QSettings("xmdm3", "xmdms").value(
            "search_attempts", 3, type=int)
        self.settings_attempts_spin.setValue(
            min(max(int(saved_attempts or 3), 3), 100))
        self.settings_theme_combo = QComboBox()
        for label, code in (("Auto", "auto"), ("Light", "light"),
                            ("Dark", "dark")):
            self.settings_theme_combo.addItem(tr(label), code)
        self.settings_theme_combo.currentIndexChanged.connect(
            self._theme_changed)
        self.settings_passwords_combo = QComboBox()
        self.settings_passwords_combo.addItem(tr("Show"), True)
        self.settings_passwords_combo.addItem(tr("Hide"), False)
        password_index = self.settings_passwords_combo.findData(
            bool(passwords_visible()))
        if password_index >= 0:
            self.settings_passwords_combo.setCurrentIndex(password_index)
        self.settings_passwords_combo.currentIndexChanged.connect(
            self._passwords_changed)
        self.settings_language_combo = QComboBox()
        self.settings_language_combo.addItem(tr("Auto"), "auto")
        self.settings_language_combo.addItem(tr("English"), "en")
        self.settings_language_combo.addItem("Русский", "ru")
        saved_language = str(QSettings("xmdm3", "xmdms").value(
            "language", "auto", type=str) or "auto").strip().lower()
        language_index = self.settings_language_combo.findData(saved_language)
        if language_index < 0:
            language_index = 0
        self.settings_language_combo.blockSignals(True)
        self.settings_language_combo.setCurrentIndex(language_index)
        self.settings_language_combo.blockSignals(False)
        self.settings_language_combo.currentIndexChanged.connect(
            self._language_changed)
        self.settings_timeout_spin.valueChanged.connect(
            lambda value: self._save_setting(
                "search_timeout", int(value)))
        self.settings_attempts_spin.valueChanged.connect(
            lambda value: self._save_setting(
                "search_attempts", int(value)))
        settings_layout = QGridLayout()
        settings_layout.addWidget(QLabel("Search timeout:"), 0, 0)
        settings_layout.addWidget(self.settings_timeout_spin, 0, 1)
        settings_layout.addWidget(QLabel("Search attempts:"), 1, 0)
        settings_layout.addWidget(self.settings_attempts_spin, 1, 1)
        settings_layout.addWidget(QLabel("Theme:"), 2, 0)
        settings_layout.addWidget(self.settings_theme_combo, 2, 1)
        settings_layout.addWidget(QLabel("Passwords:"), 3, 0)
        settings_layout.addWidget(self.settings_passwords_combo, 3, 1)
        settings_layout.addWidget(QLabel("Language:"), 4, 0)
        settings_layout.addWidget(self.settings_language_combo, 4, 1)
        settings_layout.setRowStretch(5, 1)

        about_group = QGroupBox("About")
        about_group.setStyleSheet(GROUP_BOX_STYLE)
        self.about_group = about_group
        about_layout = QVBoxLayout(about_group)
        about_layout.setSpacing(4)
        version_row = QHBoxLayout()
        self.about_version_label = QLabel(
            "XMDMS %s%s" % (
                APP_VERSION,
                " (%s)" % BUILD_COMMIT if BUILD_COMMIT else ""))
        if BUILD_DATE:
            self.about_version_label.setToolTip(
                "Build date: %s" % BUILD_DATE)
        self.about_check_button = QPushButton("Check for updates")
        self.about_check_button.clicked.connect(self._check_updates)
        version_row.addWidget(self.about_version_label)
        version_row.addStretch(1)
        version_row.addWidget(self.about_check_button)
        about_layout.addLayout(version_row)
        self.about_status_label = QLabel(tr("Not checked"))
        self.about_status_label.setProperty("i18nDynamic", True)
        self.about_status_label.setWordWrap(True)
        about_layout.addWidget(self.about_status_label)
        self.about_notes = QTextBrowser()
        self.about_notes.setOpenExternalLinks(True)
        self.about_notes.setFixedHeight(170)
        self.about_notes.setPlaceholderText(tr("No release notes."))
        about_layout.addWidget(self.about_notes)
        year = datetime.now().year
        self.about_copyright = QLabel(
            'Copyright %d <a href="%s">@dimerr</a>' % (year, GITHUB_PROFILE))
        self.about_copyright.setOpenExternalLinks(True)
        self.about_copyright.setTextFormat(Qt.TextFormat.RichText)
        self.about_copyright.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(self.about_copyright)
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        settings_layout.addWidget(separator, 6, 0, 1, 2)
        settings_layout.addWidget(about_group, 7, 0, 1, 2)
        settings_panel = QWidget()
        settings_panel.setLayout(settings_layout)
        self._settings_panel = settings_panel
        settings_scroll = QScrollArea()
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setFrameShape(QFrame.Shape.NoFrame)
        settings_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        settings_scroll.setWidget(settings_panel)
        self._settings_scroll = settings_scroll
        saved_theme = str(QSettings("xmdm3", "xmdms").value(
            "theme", "auto") or "auto").strip().lower()
        index = self.settings_theme_combo.findData(saved_theme)
        if index < 0:
            index = self.settings_theme_combo.findData("auto")
        if index >= 0:
            self.settings_theme_combo.blockSignals(True)
            self.settings_theme_combo.setCurrentIndex(index)
            self.settings_theme_combo.blockSignals(False)


        self.system_hardware_edit = QLineEdit()
        self.system_hardware_edit.setReadOnly(True)
        self.system_software_edit = QLineEdit()
        self.system_software_edit.setReadOnly(True)
        self.system_cloud_edit = QLineEdit()
        self.system_cloud_edit.setReadOnly(True)
        self.system_tv_combo = QComboBox()
        self.system_tv_combo.setEditable(True)
        self.system_tv_combo.addItems(["PAL", "NTSC"])
        self.system_language_combo = QComboBox()
        self.system_language_combo.setEditable(True)
        self.system_language_combo.addItems(
            ["English", "Russian", "Spanish", "German", "French", "Italian"])
        self.system_build_edit = QLineEdit()
        self.system_build_edit.setReadOnly(True)
        self.system_type_edit = QLineEdit()
        self.system_type_edit.setReadOnly(True)
        self.system_restart_day_combo = QComboBox()
        self.system_restart_day_combo.addItems(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        self.system_restart_day_combo.setCurrentIndex(-1)
        self.system_restart_hour_combo = QComboBox()
        for hour in range(24):
            self.system_restart_hour_combo.addItem("%02d:00" % hour, hour)
        self.system_age_edit = QLineEdit()
        self.system_age_edit.setReadOnly(True)
        self.system_channels_edit = QLineEdit()
        self.system_channels_edit.setReadOnly(True)
        self.system_channels_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.system_maxchannels_combo = QComboBox()
        self.system_nat_status_edit = QLineEdit()
        self.system_nat_status_edit.setReadOnly(True)
        self.system_nat_info_edit = QLineEdit()
        self.system_nat_info_edit.setReadOnly(True)
        self.system_timezone_combo = QComboBox()
        for label, offset in TIME_ZONE_CHOICES:
            self.system_timezone_combo.addItem(label, offset)
        self._system_timezone_config = {}
        self.system_date_combo = QComboBox()
        self.system_date_combo.setEditable(True)
        self.system_date_combo.addItems(["YYYYMMDD", "MMDDYY", "DDMMYY", "YYMMDD"])
        self.system_separator_combo = QComboBox()
        self.system_separator_combo.setEditable(True)
        self.system_separator_combo.addItems(["-", "/", "."])
        self.system_hour_combo = QComboBox()
        self.system_hour_combo.addItems(["24-hour", "12-hour"])
        self.system_beeper_check = QCheckBox("Beeper")
        self.display_face_check = QCheckBox("Face function")
        self.display_debug_check = QCheckBox("Enable debug")
        self.display_debug_check.setToolTip(
            "Ability.DeviceDesc.EnableDebugMode")
        self.display_audio_edit = QLineEdit()
        self.display_audio_edit.setReadOnly(True)
        self._system_device_desc_config = {}
        self.system_sync_button = QPushButton("Sync time")
        self.system_sync_button.clicked.connect(self._system_sync_time)
        self.system_channels_button = QPushButton("Digital channels")
        self.system_channels_button.clicked.connect(self._open_channels)
        self.system_reboot_button = QPushButton("Reboot")
        self.system_reboot_button.clicked.connect(self._system_reboot)
        self.system_import_button = QPushButton("Import config")
        self.system_import_button.clicked.connect(self._import_config)
        self.system_export_button = QPushButton("Export config")
        self.system_export_button.clicked.connect(self._export_config)
        self.system_reset_button = QPushButton("Reset config")
        self.system_reset_button.clicked.connect(self._reset_config)
        self.system_logs_button = QPushButton("View logs")
        self.system_logs_button.clicked.connect(self._view_logs)
        self.system_erase_logs_button = QPushButton("Erase logs")
        self.system_erase_logs_button.clicked.connect(self._erase_logs)
        self.system_recovery_button = QPushButton("Recovery")
        self.system_recovery_button.setToolTip(
            "Build an XM-DVR recovery image (.img) from a firmware .bin.")
        self.system_recovery_button.clicked.connect(self._recovery_image)
        self.system_dump_button = QPushButton("Dump")
        self.system_dump_button.setToolTip(
            "Build a flash dump (.dump) from the uImages in a firmware .bin.")
        self.system_dump_button.clicked.connect(self._dump_image)
        self.system_open_dir_button = QPushButton("Open dir")
        self.system_open_dir_button.setToolTip(
            "Open the application folder (configs are saved in the cfgs "
            "subfolder).")
        self.system_open_dir_button.clicked.connect(self._open_app_dir)
        self._system_general_keys = {}
        metrics = self.fontMetrics()

        def field_width(label, widget, sample=None, minimum=60):
            label_widget = QLabel(label)
            width = max(label_widget.sizeHint().width(), minimum)
            if sample:
                extra = 30 if isinstance(widget, QComboBox) else 10
                width = max(width, metrics.horizontalAdvance(sample) + extra)
            return width

        def field_block(label, widget, sample=None, minimum=60):
            label_widget = QLabel(label)
            width = field_width(label, widget, sample, minimum)
            widget.setMinimumWidth(width)
            widget.setMaximumWidth(width)
            block = QVBoxLayout()
            block.setSpacing(1)
            block.addWidget(label_widget)
            block.addWidget(widget)
            return block

        for button in (self.system_import_button, self.system_export_button,
                       self.system_reset_button, self.system_logs_button,
                       self.system_erase_logs_button,
                       self.system_recovery_button, self.system_dump_button,
                       self.system_open_dir_button):
            button.setMaximumWidth(84)

        info_grid = QGridLayout()
        info_grid.setContentsMargins(4, 4, 4, 4)
        info_grid.setHorizontalSpacing(4)

        hardware_row = QHBoxLayout()
        hardware_row.setSpacing(4)
        hardware_row.addLayout(field_block(
            "Hardware:", self.system_hardware_edit, minimum=180))
        hardware_row.addLayout(field_block(
            "Cloud ID:", self.system_cloud_edit, sample="0" * 20))
        hardware_row.addStretch(1)
        info_grid.addLayout(hardware_row, 0, 0)

        software_row = QHBoxLayout()
        software_row.setSpacing(4)
        software_row.addLayout(field_block(
            "Software:", self.system_software_edit,
            sample="V4.03.R11.00000233.12201.140000.0000000"))
        software_row.addStretch(1)
        info_grid.addLayout(software_row, 1, 0)

        info_row = QHBoxLayout()
        info_row.setSpacing(4)
        info_row.addLayout(field_block(
            "Build time:", self.system_build_edit, sample="2021-06-11 10:30:00"))
        info_row.addLayout(field_block("Age", self.system_age_edit, minimum=80))
        info_row.addLayout(field_block("Channels:", self.system_channels_edit, minimum=50))
        info_row.addLayout(field_block(
            "Type:", self.system_type_edit, sample="000000000", minimum=50))
        info_row.addStretch(1)
        info_grid.addLayout(info_row, 2, 0)

        nat_row = QHBoxLayout()
        nat_row.setSpacing(4)
        nat_row.addLayout(field_block(
            "NAT status:", self.system_nat_status_edit, sample="Connected", minimum=180))
        nat_row.addLayout(field_block(
            "NAT info:", self.system_nat_info_edit,
            minimum=160))
        nat_row.addStretch(1)
        info_grid.addLayout(nat_row, 3, 0)

        general_grid = QGridLayout()
        general_grid.setContentsMargins(4, 4, 4, 4)
        general_grid.setHorizontalSpacing(4)

        media_row = QHBoxLayout()
        media_row.setSpacing(4)
        media_row.addLayout(field_block("TV standard:", self.system_tv_combo, sample="NTSC"))
        media_row.addLayout(field_block(
            "Language:", self.system_language_combo, sample="Russian"))
        language_width = round(self.system_language_combo.maximumWidth() * 1.2)
        self.system_language_combo.setMinimumWidth(language_width)
        self.system_language_combo.setMaximumWidth(language_width)
        media_row.addLayout(field_block(
            "Restart day:", self.system_restart_day_combo, sample="Wednesday"))
        media_row.addLayout(field_block(
            "Hour:", self.system_restart_hour_combo, sample="02:00"))
        media_row.addStretch(1)
        general_grid.addLayout(media_row, 0, 0)

        format_row = QHBoxLayout()
        format_row.setSpacing(4)
        format_row.addLayout(field_block(
            "Time zone:", self.system_timezone_combo, sample="UTC+03:30"))
        format_row.addLayout(field_block(
            "Date format:", self.system_date_combo, sample="YYMMDD"))
        format_row.addLayout(field_block(
            "Separator:", self.system_separator_combo, sample="W"))
        format_row.addLayout(field_block(
            "Format:", self.system_hour_combo, sample="24-hour"))
        format_row.addLayout(field_block(
            "MaxChannels:", self.system_maxchannels_combo, sample="000", minimum=50))
        format_row.addStretch(1)
        general_grid.addLayout(format_row, 1, 0)

        format_widths = (
            field_width("Time zone:", self.system_timezone_combo, "UTC+03:30"),
            field_width("Date format:", self.system_date_combo, "YYMMDD"),
            field_width("Separator:", self.system_separator_combo, "W"),
            field_width("Format:", self.system_hour_combo, "24-hour"),
            field_width("MaxChannels:", self.system_maxchannels_combo, "000", 50),
        )
        row_left = general_grid.contentsMargins().left() + 1
        format_right = (row_left + sum(format_widths)
                        + 4 * (len(format_widths) - 1))
        maxchannels_left = format_right - format_widths[-1]

        audio_label = QLabel("AudioIn:")
        audio_block = QVBoxLayout()
        audio_block.setSpacing(1)
        audio_block.addWidget(audio_label)
        audio_block.addWidget(self.display_audio_edit)
        self.display_audio_edit.setFixedWidth(format_widths[-1])

        checkbox_row = QHBoxLayout()
        checkbox_row.setSpacing(6)
        checkbox_row.addWidget(
            self.system_beeper_check, 0, Qt.AlignmentFlag.AlignBottom)
        checkbox_row.addWidget(
            self.display_face_check, 0, Qt.AlignmentFlag.AlignBottom)
        checkbox_row.addWidget(
            self.display_debug_check, 0, Qt.AlignmentFlag.AlignBottom)
        used_left = (row_left + self.system_beeper_check.sizeHint().width()
                     + 6 + self.display_face_check.sizeHint().width()
                     + 6 + self.display_debug_check.sizeHint().width() + 6)
        checkbox_row.addSpacing(max(0, maxchannels_left - used_left))
        checkbox_row.addLayout(audio_block)
        checkbox_row.addStretch(1)
        general_grid.addLayout(checkbox_row, 2, 0)
        general_grid.setColumnStretch(0, 1)

        info_group = QGroupBox("Info")
        info_group.setStyleSheet(GROUP_BOX_STYLE)
        info_group.setLayout(info_grid)
        general_group = QGroupBox("General")
        general_group.setStyleSheet(GROUP_BOX_STYLE)
        general_group.setLayout(general_grid)

        left_buttons = QVBoxLayout()
        left_buttons.setSpacing(6)
        left_buttons.addWidget(self.system_sync_button)
        left_buttons.addWidget(self.system_channels_button)
        left_buttons.addWidget(self.system_reboot_button)
        self.system_qr_label = QLabel()
        self.system_qr_label.setFixedSize(210, 210)
        self.system_qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.system_qr_label.setStyleSheet(
            "background-color: white; border: 1px solid #BDBDBD;")
        self.system_qr_label.setVisible(False)
        left_buttons.addSpacing(8)
        left_buttons.addWidget(
            self.system_qr_label, 0, Qt.AlignmentFlag.AlignHCenter)
        left_buttons.addStretch(1)
        self.system_cloud_edit.textChanged.connect(self._update_cloud_qr)

        right_buttons = QGridLayout()
        right_buttons.setHorizontalSpacing(6)
        right_buttons.addWidget(self.system_import_button, 0, 0)
        right_buttons.addWidget(self.system_export_button, 1, 0)
        right_buttons.addWidget(self.system_reset_button, 2, 0)
        right_buttons.addWidget(self.system_logs_button, 3, 0)
        right_buttons.addWidget(self.system_erase_logs_button, 4, 0)
        right_buttons.addWidget(self.system_recovery_button, 5, 0)
        right_buttons.addWidget(self.system_dump_button, 6, 0)
        right_buttons.addWidget(self.system_open_dir_button, 7, 0)
        self.system_buttons_grid = right_buttons

        buttons_area = QHBoxLayout()
        buttons_area.setSpacing(6)
        buttons_area.addLayout(left_buttons, 1)
        buttons_area.addLayout(right_buttons, 0)

        system_layout = QVBoxLayout()
        system_layout.addWidget(info_group)
        system_layout.addWidget(general_group)
        system_layout.addLayout(buttons_area)
        system_layout.addStretch(1)
        system_panel = QWidget()
        system_panel.setLayout(system_layout)
        self.tabs.addTab(system_panel, "System")

        self.display_resolution_combo = QComboBox()
        self.display_resolution_combo.setEditable(True)
        self.display_resolution_combo.setMinimumContentsLength(16)
        self.display_resolution_combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._display_video_out_config = {}
        self._display_gui_checks = {}
        self.display_window_alpha_spin = QSpinBox()
        self.display_window_alpha_spin.setRange(0, 255)
        self._display_gui_set_config = {}

        video_out_group = QGroupBox("Video out")
        video_out_group.setStyleSheet(GROUP_BOX_STYLE)
        video_out_layout = QHBoxLayout(video_out_group)
        video_out_layout.addWidget(QLabel("Resolution:"))
        video_out_layout.addWidget(self.display_resolution_combo)
        video_out_layout.addStretch(1)

        gui_group = QGroupBox("GUI set")
        gui_group.setStyleSheet(GROUP_BOX_STYLE)
        gui_grid = QGridLayout(gui_group)
        gui_grid.setHorizontalSpacing(6)
        gui_grid.setVerticalSpacing(3)
        for index, key in enumerate(GUI_SET_KEYS):
            check = QCheckBox(key)
            check.setEnabled(False)
            self._display_gui_checks[key] = check
            gui_grid.addWidget(check, index // 2, index % 2)
        alpha_row = QHBoxLayout()
        alpha_row.addWidget(QLabel("Window alpha:"))
        alpha_row.addWidget(self.display_window_alpha_spin)
        alpha_row.addStretch(1)
        gui_grid.addLayout(alpha_row, (len(GUI_SET_KEYS) + 1) // 2, 0, 1, 2)

        display_layout = QVBoxLayout()
        display_layout.addWidget(video_out_group)
        display_layout.addWidget(gui_group)
        display_layout.addStretch(1)
        display_panel = QWidget()
        display_panel.setLayout(display_layout)
        self.tabs.addTab(display_panel, "Display")

        self.encode_channel_combo = QComboBox()
        self.encode_channel_combo.currentIndexChanged.connect(self._encode_channel_changed)
        self.encode_widgets = {}
        self._build_encode_fields()
        self._encode_mode = None
        self._encode_configs = []
        self._encode_av_enc = None
        self._encode_av_entries = []
        self._encode_smart = []
        self._encode_ability = []
        self._encode_current = None
        self._encode_max_fps = 25
        self._encode_resolution_names = []
        self._encode_channel_names = []

        encode_grid = QGridLayout()
        encode_grid.setHorizontalSpacing(8)
        encode_grid.setVerticalSpacing(3)
        encode_grid.addWidget(QLabel("Channel:"), 0, 0)
        encode_grid.addWidget(self.encode_channel_combo, 0, 1, 1, 2)
        self.encode_table_button = QPushButton("All channels")
        self.encode_table_button.clicked.connect(self._open_encode_table)
        self.encode_table_button.setEnabled(False)
        encode_grid.addWidget(self.encode_table_button, 0, 3)
        encode_grid.addWidget(QLabel("Main stream"), 1, 1)
        encode_grid.addWidget(QLabel("Substream"), 1, 2)
        encode_grid.setColumnStretch(1, 1)
        encode_grid.setColumnStretch(2, 1)
        row_labels = (("Compression", "codec"), ("Resolution", "res"), ("FPS", "fps"),
                      ("RC type", "rc"), ("Quality", "quality"), ("Bitrate", "bitrate"),
                      ("I-frame int", "gop"))
        row = 2
        for label, key in row_labels:
            encode_grid.addWidget(QLabel(label + ":"), row, 0)
            encode_grid.addWidget(self.encode_widgets["main"][key], row, 1)
            encode_grid.addWidget(self.encode_widgets["sub"][key], row, 2)
            row += 1
        encode_grid.addWidget(QLabel("Enable:"), row, 0)
        for prefix, column in (("main", 1), ("sub", 2)):
            box = QHBoxLayout()
            box.setSpacing(6)
            box.addWidget(self.encode_widgets[prefix]["video"])
            box.addWidget(self.encode_widgets[prefix]["audio"])
            box.addStretch(1)
            encode_grid.addLayout(box, row, column)
        row += 1
        encode_grid.addWidget(QLabel("Smart encode:"), row, 0)
        encode_grid.addWidget(self.encode_widgets["main"]["smart"], row, 1)
        encode_grid.addWidget(self.encode_widgets["sub"]["smart"], row, 2)
        encode_grid.setRowStretch(row + 1, 1)

        self.encode_summary_group = QGroupBox("Channels")
        self.encode_summary_group.setStyleSheet(GROUP_BOX_STYLE)
        self.encode_summary_grid = QGridLayout(self.encode_summary_group)
        self.encode_summary_grid.setContentsMargins(4, 4, 4, 4)
        self.encode_summary_grid.setHorizontalSpacing(10)
        self.encode_summary_grid.setVerticalSpacing(2)
        self.encode_summary_group.setVisible(False)

        encode_panel = QWidget()
        encode_layout = QVBoxLayout(encode_panel)
        encode_layout.setContentsMargins(4, 4, 4, 4)
        encode_layout.addLayout(encode_grid)
        encode_layout.addWidget(self.encode_summary_group)
        encode_layout.addStretch(1)
        self.tabs.addTab(encode_panel, "Encode")

        self.camera_channel_combo = QComboBox()
        self.camera_channel_combo.currentIndexChanged.connect(self._camera_channel_changed)
        self.camera_widgets = {}
        self.camera_ex_widgets = {}
        self._camera_configs = []
        self._camera_ex_configs = []
        self._white_light_configs = []
        self._camera_indexed = False
        self._camera_current = None
        camera_grid = QGridLayout()
        camera_grid.setHorizontalSpacing(8)
        camera_grid.setVerticalSpacing(3)
        camera_grid.addWidget(QLabel("Channel:"), 0, 0)
        camera_grid.addWidget(self.camera_channel_combo, 0, 1, 1, 3)
        camera_fields = (
            ("Day/Night", "DayNightColor", "combo",
             (("Starlight", 0), ("Color", 1), ("B&W", 2), ("HumanSense", 3),
              ("ColorSense", 4), ("SmartExir", 5), ("LicensePlate", 6))),
            ("White balance", "WhiteBalance", "combo",
             (("Auto", 0), ("Indoor", 1), ("Outdoor", 2))),
            ("BLC", "BLCMode", "combo",
             (("Close", 0), ("Open", 1))),
            ("Aperture", "ApertureMode", "combo", (("Close", 0), ("Open", 1))),
            ("Exposure level", "ExposureLevel", "spin", (0, 15)),
            ("Shutter", "EsShutter", "combo",
             (("None", 0), ("Low", 1), ("Mid", 2), ("High", 3))),
            ("Auto gain", "AutoGain", "check", None),
            ("Gain", "Gain", "spin", (0, 100)),
            ("Elec level", "ElecLevel", "spin", (0, 100)),
            ("AE sensitivity", "AeSensitivity", "spin", (1, 10)),
            ("Day NF level", "Day_nfLevel", "spin", (0, 5)),
            ("Night NF level", "Night_nfLevel", "spin", (0, 5)),
            ("IR-CUT mode", "IRCUTMode", "combo",
             (("Sync switch", 0), ("Auto switch", 1))),
            ("DNC threshold", "DncThr", "spin", (0, 100)),
        )
        for index, (label, key, kind, extra) in enumerate(camera_fields):
            column = (index % 2) * 2
            row = 1 + index // 2
            if kind == "combo":
                widget = QComboBox()
                for text, value in extra:
                    widget.addItem(text, value)
            elif kind == "spin":
                widget = QSpinBox()
                widget.setRange(extra[0], extra[1])
            else:
                widget = QCheckBox()
            self.camera_widgets[key] = widget
            camera_grid.addWidget(QLabel(label + ":"), row, column)
            camera_grid.addWidget(widget, row, column + 1)
        camera_grid.setColumnStretch(1, 1)
        camera_grid.setColumnStretch(3, 1)

        ex_row = 1 + (len(camera_fields) + 1) // 2
        automatic = QSpinBox()
        automatic.setRange(1, 5)
        automatic.setToolTip("Camera.ParamEx.AutomaticAdjustment")
        self.camera_ex_widgets["AutomaticAdjustment"] = automatic
        style = QComboBox()
        for text, value in (("Style 1", "typedefault"),
                            ("Style 2", "style1"),
                            ("Style 3", "style2")):
            style.addItem(text, value)
        style.setToolTip("Camera.ParamEx.Style")
        self.camera_ex_widgets["Style"] = style
        camera_grid.addWidget(QLabel("DN switch:"), ex_row, 0)
        camera_grid.addWidget(automatic, ex_row, 1)
        camera_grid.addWidget(QLabel("Style:"), ex_row, 2)
        camera_grid.addWidget(style, ex_row, 3)

        dwdr = QCheckBox()
        dwdr.setToolTip("Camera.ParamEx.BroadTrends.AutoGain")
        self.camera_ex_widgets["DWDR"] = dwdr
        dwdr_gain = QSpinBox()
        dwdr_gain.setRange(0, 100)
        dwdr_gain.setToolTip("Camera.ParamEx.BroadTrends.Gain")
        self.camera_ex_widgets["DWDRGain"] = dwdr_gain
        dwdr_row = ex_row + 1
        dwdr_box = QWidget()
        dwdr_layout = QHBoxLayout(dwdr_box)
        dwdr_layout.setContentsMargins(0, 0, 0, 0)
        dwdr_layout.setSpacing(6)
        dwdr_layout.addWidget(dwdr)
        dwdr_layout.addWidget(QLabel("Strength:"))
        dwdr_layout.addWidget(dwdr_gain)
        dwdr_layout.addStretch(1)
        camera_grid.addWidget(QLabel("DWDR:"), dwdr_row, 0)
        camera_grid.addWidget(dwdr_box, dwdr_row, 1, 1, 3)
        camera_grid.setRowStretch(dwdr_row + 1, 1)

        image_layout = QHBoxLayout()
        for key, label in (("PictureFlip", "Flip"),
                           ("PictureMirror", "Mirror"),
                           ("IrcutSwap", "IR-CUT swap"),
                           ("RejectFlicker", "Reject flicker")):
            box = QCheckBox(label)
            self.camera_widgets[key] = box
            image_layout.addWidget(box)
        image_layout.addStretch(1)
        self.white_light_widgets = {}
        white_group = QGroupBox("White light")
        white_group.setStyleSheet(GROUP_BOX_STYLE)
        white_grid = QGridLayout(white_group)
        white_grid.setHorizontalSpacing(8)
        white_grid.setVerticalSpacing(3)
        white_fields = (
            ("Work mode", "WorkMode", "combo",
             (("Steady Mode", "KeepOpen"), ("Auto Mode", "Auto"),
              ("Timer Mode", "Timing"), ("Smart Mode", "Intelligent"),
              ("Atmosphere Light", "Atmosphere"), ("Music Mode", "Glint"),
              ("Off", "Close"))),
            ("Brightness", "Brightness", "spin", (0, 100)),
            ("Trigger level", "MoveTrigLevel", "spin", (0, 5)),
            ("Trigger duration", "MoveTrigDuration", "spin", (0, 120)),
            ("Period enable", "PeriodEnable", "check", None),
            ("Start hour", "StartHour", "spin", (0, 23)),
            ("Start minute", "StartMinute", "spin", (0, 59)),
            ("End hour", "EndHour", "spin", (0, 23)),
            ("End minute", "EndMinute", "spin", (0, 59)),
        )
        for index, (label, key, kind, extra) in enumerate(white_fields):
            column = (index % 2) * 2
            row = index // 2
            if kind == "combo":
                widget = QComboBox()
                for text, value in extra:
                    widget.addItem(text, value)
            elif kind == "spin":
                widget = QSpinBox()
                widget.setRange(extra[0], extra[1])
            else:
                widget = QCheckBox()
            self.white_light_widgets[key] = widget
            white_grid.addWidget(QLabel(label + ":"), row, column)
            white_grid.addWidget(widget, row, column + 1)
        white_grid.setColumnStretch(1, 1)
        white_grid.setColumnStretch(3, 1)

        camera_panel = QWidget()
        camera_layout = QVBoxLayout(camera_panel)
        camera_layout.setContentsMargins(4, 4, 4, 4)
        camera_layout.addLayout(camera_grid)
        camera_layout.addLayout(image_layout)
        camera_layout.addWidget(white_group)
        camera_layout.addStretch(1)
        self.tabs.addTab(camera_panel, "Camera")

        self.storage_table = QTableWidget(0, len(STORAGE_COLUMNS))
        self.storage_table.setHorizontalHeaderLabels(STORAGE_COLUMNS)
        install_copy_menu(self.storage_table)
        self.storage_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.storage_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.storage_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.storage_table.setAlternatingRowColors(True)
        storage_header = self.storage_table.horizontalHeader()
        storage_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        storage_header.setStretchLastSection(False)
        self.storage_table.verticalHeader().setVisible(False)
        self.storage_table.setMaximumHeight(
            self.storage_table.horizontalHeader().height()
            + self.storage_table.verticalHeader().defaultSectionSize() * 8
            + self.storage_table.frameWidth() * 2 + 2)
        self._storage_parts = []

        storage_buttons = QGridLayout()
        storage_buttons.setHorizontalSpacing(6)
        storage_actions = (
            ("Read/Write", lambda: self._storage_set_type("ReadWrite")),
            ("Read only", lambda: self._storage_set_type("ReadOnly")),
            ("Redundant", lambda: self._storage_set_type("Redundant")),
            ("Snapshot", lambda: self._storage_set_type("SnapShot")),
            ("Format", lambda: self._storage_action(
                "Clear", confirm="Format disk", label="Formatting disk on")),
            ("Recover", lambda: self._storage_action(
                "Recover", confirm="Recover disk", label="Recovering disk on")),
        )
        for index, (label, handler) in enumerate(storage_actions):
            button = QPushButton(label)
            button.clicked.connect(handler)
            storage_buttons.addWidget(button, index // 3, index % 3)
        storage_buttons.setColumnStretch(3, 1)

        storage_layout = QVBoxLayout()
        storage_layout.setContentsMargins(4, 4, 4, 4)
        storage_layout.addWidget(self.storage_table)
        storage_layout.addLayout(storage_buttons)
        storage_layout.addStretch(1)
        storage_panel = QWidget()
        storage_panel.setLayout(storage_layout)
        self.tabs.addTab(storage_panel, "Storage")

        def uart_combo(values):
            combo = QComboBox()
            for value in values:
                combo.addItem(str(value), value)
            return combo

        self.rs232_function_combo = QComboBox()
        self.rs232_baud_combo = uart_combo(SERIAL_BAUD_RATES)
        self.rs232_databits_combo = uart_combo(SERIAL_DATA_BITS)
        self.rs232_stopbits_combo = uart_combo(SERIAL_STOP_BITS)
        self.rs232_parity_combo = uart_combo(SERIAL_PARITY)
        rs232_group = QGroupBox("RS232")
        rs232_group.setStyleSheet(GROUP_BOX_STYLE)
        rs232_grid = QGridLayout(rs232_group)
        rs232_grid.setHorizontalSpacing(8)
        rs232_grid.setVerticalSpacing(3)
        rs232_fields = (("Function", self.rs232_function_combo),
                        ("Baud rate", self.rs232_baud_combo),
                        ("Data bits", self.rs232_databits_combo),
                        ("Stop bits", self.rs232_stopbits_combo),
                        ("Parity", self.rs232_parity_combo))
        for index, (label, widget) in enumerate(rs232_fields):
            column = (index % 2) * 2
            row = index // 2
            rs232_grid.addWidget(QLabel(label + ":"), row, column)
            rs232_grid.addWidget(widget, row, column + 1)
        rs232_grid.setColumnStretch(1, 1)
        rs232_grid.setColumnStretch(3, 1)

        self.ptz_channel_combo = QComboBox()
        self.ptz_channel_combo.currentIndexChanged.connect(self._ptz_channel_changed)
        self.ptz_protocol_combo = QComboBox()
        self.ptz_address_spin = QSpinBox()
        self.ptz_address_spin.setRange(0, 255)
        self.ptz_baud_combo = uart_combo(SERIAL_BAUD_RATES)
        self.ptz_databits_combo = uart_combo(SERIAL_DATA_BITS)
        self.ptz_stopbits_combo = uart_combo(SERIAL_STOP_BITS)
        self.ptz_parity_combo = uart_combo(SERIAL_PARITY)
        self._uart_comm = None
        self._uart_ptz = None
        self._uart_rs485 = None
        self._ptz_current = None
        ptz_group = QGroupBox("PTZ")
        ptz_group.setStyleSheet(GROUP_BOX_STYLE)
        ptz_grid = QGridLayout(ptz_group)
        ptz_grid.setHorizontalSpacing(8)
        ptz_grid.setVerticalSpacing(3)
        ptz_grid.addWidget(QLabel("Channel:"), 0, 0)
        ptz_grid.addWidget(self.ptz_channel_combo, 0, 1)
        ptz_fields = (("Protocol", self.ptz_protocol_combo),
                      ("Address", self.ptz_address_spin),
                      ("Baud rate", self.ptz_baud_combo),
                      ("Data bits", self.ptz_databits_combo),
                      ("Stop bits", self.ptz_stopbits_combo),
                      ("Parity", self.ptz_parity_combo))
        for index, (label, widget) in enumerate(ptz_fields):
            column = (index % 2) * 2
            row = 1 + index // 2
            ptz_grid.addWidget(QLabel(label + ":"), row, column)
            ptz_grid.addWidget(widget, row, column + 1)
        ptz_grid.setColumnStretch(1, 1)
        ptz_grid.setColumnStretch(3, 1)

        self.rs485_protocol_combo = QComboBox()
        self.rs485_address_spin = QSpinBox()
        self.rs485_address_spin.setRange(0, 255)
        self.rs485_baud_combo = uart_combo(SERIAL_BAUD_RATES)
        self.rs485_databits_combo = uart_combo(SERIAL_DATA_BITS)
        self.rs485_stopbits_combo = uart_combo(SERIAL_STOP_BITS)
        self.rs485_parity_combo = uart_combo(SERIAL_PARITY)
        rs485_group = QGroupBox("RS485")
        rs485_group.setStyleSheet(GROUP_BOX_STYLE)
        rs485_grid = QGridLayout(rs485_group)
        rs485_grid.setHorizontalSpacing(8)
        rs485_grid.setVerticalSpacing(3)
        rs485_fields = (("Protocol", self.rs485_protocol_combo),
                        ("Address", self.rs485_address_spin),
                        ("Baud rate", self.rs485_baud_combo),
                        ("Data bits", self.rs485_databits_combo),
                        ("Stop bits", self.rs485_stopbits_combo),
                        ("Parity", self.rs485_parity_combo))
        for index, (label, widget) in enumerate(rs485_fields):
            column = (index % 2) * 2
            row = index // 2
            rs485_grid.addWidget(QLabel(label + ":"), row, column)
            rs485_grid.addWidget(widget, row, column + 1)
        rs485_grid.setColumnStretch(1, 1)
        rs485_grid.setColumnStretch(3, 1)

        serial_layout = QVBoxLayout()
        serial_layout.setContentsMargins(4, 4, 4, 4)
        serial_layout.addWidget(rs232_group)
        serial_layout.addWidget(ptz_group)
        serial_layout.addWidget(rs485_group)
        serial_layout.addStretch(1)
        serial_panel = QWidget()
        serial_panel.setLayout(serial_layout)
        self.tabs.addTab(serial_panel, "RS232/485/PTZ")

        self.users_table = QTableWidget(0, 3)
        self.users_table.setHorizontalHeaderLabels(("#", "Name", "Group"))
        install_copy_menu(self.users_table)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.users_table.setAlternatingRowColors(True)
        users_header = self.users_table.horizontalHeader()
        users_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        users_header.setStretchLastSection(True)
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setMaximumHeight(
            self.users_table.horizontalHeader().height()
            + self.users_table.verticalHeader().defaultSectionSize() * 8
            + self.users_table.frameWidth() * 2 + 2)

        self.groups_table = QTableWidget(0, 2)
        self.groups_table.setHorizontalHeaderLabels(("#", "Group"))
        install_copy_menu(self.groups_table)
        self.groups_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.groups_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.groups_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.groups_table.setAlternatingRowColors(True)
        groups_header = self.groups_table.horizontalHeader()
        groups_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        groups_header.setStretchLastSection(True)
        self.groups_table.verticalHeader().setVisible(False)
        self.groups_table.setMaximumHeight(
            self.groups_table.horizontalHeader().height()
            + self.groups_table.verticalHeader().defaultSectionSize() * 4
            + self.groups_table.frameWidth() * 2 + 2)

        self._users = []
        self._groups = []
        self._authorities = []
        users_buttons = QGridLayout()
        users_buttons.setHorizontalSpacing(6)
        users_buttons.setVerticalSpacing(3)
        users_actions = (
            ("Refresh", self._users_refresh),
            ("Add user", self._user_add),
            ("Modify user", self._user_modify),
            ("Delete user", self._user_delete),
            ("Modify PW", self._user_password),
        )
        for index, (label, handler) in enumerate(users_actions):
            button = QPushButton(label)
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(handler)
            users_buttons.addWidget(button, index // 3, index % 3)
        for column in range(3):
            users_buttons.setColumnStretch(column, 1)
        groups_buttons = QGridLayout()
        groups_buttons.setHorizontalSpacing(6)
        groups_buttons.setVerticalSpacing(3)
        groups_actions = (
            ("Add group", self._group_add),
            ("Modify group", self._group_modify),
            ("Delete group", self._group_delete),
        )
        for index, (label, handler) in enumerate(groups_actions):
            button = QPushButton(label)
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(handler)
            groups_buttons.addWidget(button, 0, index)
        for column in range(3):
            groups_buttons.setColumnStretch(column, 1)

        users_layout = QVBoxLayout()
        users_layout.setContentsMargins(4, 4, 4, 4)
        users_layout.addWidget(QLabel("Users:"))
        users_layout.addWidget(self.users_table)
        users_layout.addLayout(users_buttons)
        users_layout.addWidget(QLabel("Groups:"))
        users_layout.addWidget(self.groups_table)
        users_layout.addLayout(groups_buttons)
        users_layout.addStretch(1)
        users_panel = QWidget()
        users_panel.setLayout(users_layout)
        self.tabs.addTab(users_panel, "Users")
        self.tabs.addTab(settings_scroll, "Settings")

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._save_current_tab)
        self.console_button = QPushButton("Console")
        self.console_button.clicked.connect(self._open_console)
        bottom_bar = QHBoxLayout()
        bottom_bar.addWidget(self.save_button)
        bottom_bar.addWidget(self.console_button)
        bottom_bar.addStretch(1)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.tabs, 1)
        right_layout.addLayout(bottom_bar)

        right_panel.setFixedWidth(470)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(table_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([900, 470])

        layout = QVBoxLayout()
        layout.addLayout(controls)
        layout.addWidget(splitter, 1)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.setSizeGripEnabled(False)
        self.video_status_label = QLabel("")
        self.video_status_label.setProperty("i18nDynamic", True)
        self.video_status_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard)
        self.connection_label = QLabel(tr("Disconnected"))
        self.connection_label.setProperty(
            "_i18n_label_source", "Disconnected")
        self.connection_label.setProperty(
            "_i18n_label_last", tr("Disconnected"))
        self.fetch_label = QLabel("")
        self.fetch_label.setProperty("i18nDynamic", True)
        for label in (self.fetch_label, self.status_label, self.video_status_label):
            label.setSizePolicy(
                QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.connection_label.setFixedWidth(
            self.fontMetrics().horizontalAdvance("Connected: 255.255.255.255") + 12)

        def status_separator():
            line = QFrame()
            line.setFrameShape(QFrame.Shape.VLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            return line

        self.middle_stack = QStackedWidget()
        self.middle_stack.addWidget(self.status_label)
        self.middle_stack.addWidget(self.video_status_label)
        self.middle_stack.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(4, 0, 4, 0)
        status_layout.setSpacing(6)
        status_layout.addWidget(self.fetch_label, 4)
        status_layout.addWidget(status_separator())
        status_layout.addWidget(self.middle_stack, 6)
        status_layout.addWidget(status_separator())
        status_layout.addWidget(self.connection_label)
        self.status_bar.addPermanentWidget(status_widget, 1)
        self.video_panel.status_changed.connect(self._on_video_status)
        self.video_panel.notice.connect(self._message)
        self.video_panel.lost.connect(self._on_video_lost)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.tabs.currentChanged.connect(self._on_settings_tab)
        self._disable_device_tabs()
        load_private_extension(self)
        retranslate_widgets(self)
        self._update_language_combo_labels()
        self._fit_system_buttons()

    def _message(self, text):
        self.fetch_label.setText(tr(text))

    def _on_video_status(self, text):
        self.video_status_label.setText(text)
        if text:
            self.middle_stack.setCurrentWidget(self.video_status_label)

    def _refresh_status_text(self):
        count = self.model.rowCount()
        base = (self._status_text if self._thread is not None
                and self._thread.isRunning() else self._idle_text)
        return "%s — %d %s" % (tr(base), count, tr("device(s)"))

    def _set_status(self, text):
        self._status_text = text
        self.status_label.setText(self._refresh_status_text())

    def _toggle_search(self, checked):
        source = "Stop" if checked else "Search"
        self.search_button.setProperty("_i18n_button_source", source)
        self.search_button.setProperty("_i18n_button_last", tr(source))
        self.search_button.setText(tr(source))
        self.interface_combo.setEnabled(not checked)
        if checked:
            self._start_search()
        else:
            self._stop_search()

    def _start_search(self):
        interface = self.interface_combo.currentData()
        if not isinstance(interface, dict):
            return
        thread = DiscoveryThread(
            interface["ip"], interface["broadcast"],
            duration=self.settings_timeout_spin.value(),
            min_probes=self.settings_attempts_spin.value(), parent=self)
        thread.device_found.connect(self._on_device_found)
        thread.status_changed.connect(self._set_status)
        thread.failed.connect(self._on_search_failed)
        thread.finished.connect(self._on_search_finished)
        self._thread = thread
        self._search_seen = set()
        self._search_devices = {}
        self._search_error = False
        self._set_status("Searching")
        thread.start()

    def _on_search_failed(self, text):
        self._search_error = True
        self._on_failed(text)

    def _on_search_finished(self):
        thread = self.sender()
        if thread is not self._thread:
            return
        self._thread = None
        thread.deleteLater()
        if self.search_button.isChecked():
            self.search_button.setChecked(False)
        removed = 0 if self._search_error else self._prune_missing_devices()
        self._idle_text = ("Search finished — removed %d device(s)" % removed
                           if removed else "Search finished")
        self.status_label.setText(self._refresh_status_text())

    def _device_replaced_at_ip(self, device):
        """True when another (different MAC) device answered on this IP."""
        ip = str(device.get("ip") or "").strip()
        if not ip:
            return False
        mac = str(device.get("mac") or "").strip().lower()
        for seen in self._search_devices.values():
            if str(seen.get("ip") or "").strip() != ip:
                continue
            seen_mac = str(seen.get("mac") or "").strip().lower()
            if mac and seen_mac and seen_mac != mac:
                return True
        return False

    def _prune_missing_devices(self):
        """Drop broadcast devices that did not answer the last search."""
        removed = 0
        for row in range(self.model.rowCount() - 1, -1, -1):
            device = self.model.device_at(row)
            if not isinstance(device, dict) or device.get("manual"):
                continue
            identity = DeviceTableModel.identity(device)
            if identity in self._search_seen:
                continue
            if identity == self._connected_identity:
                if not self._device_replaced_at_ip(device):
                    continue
                self._drop_connection()
            self.model.remove_device(row)
            removed += 1
        return removed

    def _stop_search(self):
        thread = self._thread
        self._thread = None
        if thread is not None:
            thread.stop()
            thread.wait(3000)
            thread.deleteLater()
        self._idle_text = "Stopped"
        if self.search_button.isChecked():
            self.search_button.setChecked(False)
        self.status_label.setText(self._refresh_status_text())

    def _pause_search(self):
        thread = self._thread
        self._thread = None
        if thread is not None:
            thread.stop()
            thread.wait(3000)
            thread.deleteLater()
            self._paused = True
        self.status_label.setText(self._refresh_status_text())

    def _resume_search(self):
        if self._paused:
            self._paused = False
            if self.search_button.isChecked():
                self._start_search()

    def _on_device_found(self, device):
        if isinstance(device, dict):
            identity = DeviceTableModel.identity(device)
            self._search_seen.add(identity)
            self._search_devices[identity] = device
        self.model.upsert(device)
        self.status_label.setText(self._refresh_status_text())

    def _wifi_scan(self):
        device = self._system_target()
        if not isinstance(device, dict):
            self._message("No device selected — pick a table row first.")
            return
        self._start_system_action(
            "wifi_scan", device=device, label="Scanning Wi-Fi on",
            on_fetched=self._on_wifi_scan)

    def _on_wifi_scan(self, payload):
        reply = payload.get("wifi_scan") if isinstance(payload, dict) else None
        info = reply.get("WifiAP") if isinstance(reply, dict) else None
        if isinstance(info, dict):
            entries = info.get("WifiAP")
        elif isinstance(info, list):
            entries = info
        else:
            entries = None
        if not isinstance(entries, list):
            self._message("Wi-Fi scan returned no networks.")
            return
        combo = self.network_wifi_ssid_edit
        current = combo.currentText()
        combo.blockSignals(True)
        combo.clear()
        count = 0
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            ssid = str(entry.get("SSID") or "").strip()
            if not ssid:
                continue
            combo.addItem(ssid)
            index = combo.count() - 1
            combo.setItemData(index, entry, Qt.ItemDataRole.UserRole)
            combo.setItemData(
                index,
                "Signal: %s | Sec: %s | Enc: %s" % (
                    entry.get("RSSI") or "?",
                    entry.get("Auth") or "?",
                    entry.get("EncrypType") or "?"),
                Qt.ItemDataRole.ToolTipRole)
            count += 1
        if current and combo.findText(current) < 0:
            combo.addItem(current)
        combo.setCurrentText(current)
        combo.blockSignals(False)
        self._message("Wi-Fi scan: %d network(s)" % count)

    @staticmethod
    def _select_combo_text(combo, value):
        text = str(value or "").strip()
        if not text:
            return
        for index in range(combo.count()):
            if combo.itemText(index).casefold() == text.casefold():
                combo.setCurrentIndex(index)
                return
        combo.addItem(text)
        combo.setCurrentIndex(combo.count() - 1)

    def _wifi_ssid_activated(self, index):
        entry = self.network_wifi_ssid_edit.itemData(
            index, Qt.ItemDataRole.UserRole)
        if not isinstance(entry, dict):
            return
        self._select_combo_text(
            self.network_wifi_auth_combo, entry.get("Auth"))
        self._select_combo_text(
            self.network_wifi_encrypt_combo, entry.get("EncrypType"))
        self._select_combo_text(
            self.network_wifi_nettype_combo, entry.get("NetType"))
        ssid = self.network_wifi_ssid_edit.itemText(index)
        self._message("Wi-Fi %s: %s / %s" % (
            ssid, entry.get("Auth") or "?", entry.get("EncrypType") or "?"))

    def _set_default_dns(self):
        self.network_dns1_edit.setValue("77.88.8.8")
        self.network_dns2_edit.setValue("1.1.1.1")

    def _fill_network_fields(self, device):
        if not isinstance(device, dict):
            return
        raw = device.get("raw") or {}
        self.network_name_edit.setText(str(raw.get("HostName") or device.get("host_name") or ""))
        self.network_address_edit.setValue(device.get("ip") or "")
        self.network_submask_edit.setValue(device.get("subnet") or "")
        self.network_gateway_edit.setValue(device.get("gateway") or "")
        self.network_dns1_edit.setValue(format_ipv4(raw.get("DNS1") or raw.get("Dns1")))
        self.network_dns2_edit.setValue(format_ipv4(raw.get("DNS2") or raw.get("Dns2")))
        self.network_adaptive_check.setChecked(bool(raw.get("IPAdaptive")))
        self.network_dhcp_check.setChecked(bool(raw.get("Enable")))
        self.network_http_edit.setText(str(device.get("http_port") or 80))
        self.network_tcp_edit.setText(str(device.get("tcp_port") or 34567))

    def _fill_network_from_fetch(self, common, dhcp, adaptive, dns,
                                 smartnet=None, general=None, wifi=None, rtsp=None,
                                 upgrade=None, upnp=None, onvif_pwd=None, pms=None,
                                 ntp=None, pubcfg=None, caps=None, force_dhcp=None,
                                 disable_xm_server=None, nat=None, ability=None,
                                 oemcfg=None):
        if isinstance(common, dict) and common:
            self.network_name_edit.setText(str(common.get("HostName") or ""))
            self.network_address_edit.setValue(format_ipv4(common.get("HostIP")))
            self.network_submask_edit.setValue(format_ipv4(common.get("Submask")))
            self.network_gateway_edit.setValue(
                format_ipv4(common.get("GateWay") or common.get("Gateway")))
            try:
                self.network_http_edit.setText(str(common.get("HttpPort") or 80))
            except (TypeError, ValueError):
                pass
            try:
                self.network_tcp_edit.setText(str(common.get("TCPPort") or 34567))
            except (TypeError, ValueError):
                pass
            transfer = str(common.get("TransferPlan") or "")
            if transfer:
                if self.network_transfer_combo.findText(transfer) < 0:
                    self.network_transfer_combo.addItem(transfer)
                self.network_transfer_combo.setCurrentText(transfer)
            self.network_hsdownload_check.setChecked(bool(common.get("UseHSDownLoad")))
        if isinstance(dns, dict) and dns:
            self.network_dns1_edit.setValue(format_ipv4(
                dns.get("Address") or dns.get("DNS1") or dns.get("Dns1")))
            self.network_dns2_edit.setValue(format_ipv4(
                dns.get("SpareAddress") or dns.get("DNS2") or dns.get("Dns2")))
        if isinstance(dhcp, list):
            self._network_dhcp_config = dhcp
            entry = next(
                (item for item in dhcp if isinstance(item, dict) and item.get("Enable")),
                next((item for item in dhcp if isinstance(item, dict)), {}))
            self.network_dhcp_check.setChecked(bool(entry.get("Enable")))
        elif isinstance(dhcp, dict):
            self._network_dhcp_config = [dhcp]
            self.network_dhcp_check.setChecked(bool(dhcp.get("Enable")))
        if isinstance(adaptive, dict):
            self.network_adaptive_check.setChecked(bool(adaptive.get("IPAdaptive")))
        project = general.get("ProjectMode") if isinstance(general, dict) else None
        if isinstance(project, dict):
            project = project.get("Enable")
        if project is not None:
            self.network_smartnet_check.setChecked(not bool(project))
        if isinstance(smartnet, dict):
            self.network_smartnet_auto_check.setChecked(bool(smartnet.get("Enable")))
            self.network_smartnet_change_ip_check.setChecked(bool(smartnet.get("bChangeIP")))
        if isinstance(rtsp, dict) and rtsp:
            self._network_rtsp_config = rtsp
            server = rtsp.get("Server") if isinstance(rtsp.get("Server"), dict) else {}
            try:
                self.network_rtsp_edit.setText(str(server.get("Port") or 554))
            except (TypeError, ValueError):
                pass
        if isinstance(upgrade, dict) and upgrade:
            self._network_upgrade_config = upgrade
            self.upgrade_group.setChecked(bool(upgrade.get("Enable")))
            self.network_upgrade_server_edit.setText(str(upgrade.get("ServerAddr") or ""))
            try:
                self.network_upgrade_port_edit.setText(str(upgrade.get("ServerPort") or 8083))
            except (TypeError, ValueError):
                pass
            self.network_upgrade_autocheck_check.setChecked(bool(upgrade.get("AutoCheck")))
            self.network_upgrade_autoimp_check.setChecked(bool(upgrade.get("AutoUpgradeImp")))
            self.network_upgrade_ignore_all_check.setChecked(bool(upgrade.get("IgnoreAllVersion")))
            self.network_upgrade_ignore_time_check.setChecked(bool(upgrade.get("IgnoreCurTime")))
            self.network_upgrade_ignore_version_check.setChecked(bool(upgrade.get("IgnoreCurVersion")))
            self.network_upgrade_just_imp_check.setChecked(bool(upgrade.get("JustImpVersion")))
        if isinstance(upnp, dict) and upnp:
            self._network_upnp_config = upnp
            self.network_upnp_check.setChecked(bool(upnp.get("Enable")))
        if isinstance(onvif_pwd, dict) and onvif_pwd:
            self._network_onvif_pwd_config = onvif_pwd
            self.network_onvif_pwd_check.setChecked(bool(onvif_pwd.get("Enable")))
        if isinstance(pms, dict) and pms:
            self._network_pms_config = pms
            self.network_pms_check.setChecked(bool(pms.get("Enable")))
        if isinstance(ntp, dict) and ntp:
            self._network_ntp_config = ntp
            self.ntp_group.setChecked(bool(ntp.get("Enable")))
            server = ntp.get("Server") if isinstance(ntp.get("Server"), dict) else {}
            manual = ntp.get("TimeZone") == 13
            self.network_ntp_manual_radio.setChecked(manual)
            self.network_ntp_auto_radio.setChecked(not manual)
            self.network_ntp_server_edit.setEnabled(manual)
            self.network_ntp_server_edit.setText(str(server.get("Name") or ""))
            try:
                self.network_ntp_period_edit.setText(str(ntp.get("UpdatePeriod") or 60))
            except (TypeError, ValueError):
                pass
        if isinstance(pubcfg, dict) and pubcfg:
            self.network_pubcfg_edit.setText(str(pubcfg.get("NetPub-Cfg") or ""))
        if isinstance(caps, dict) and caps:
            self.network_caps_edit.setText(str(caps.get("NetCaps") or ""))
        if isinstance(force_dhcp, dict) and force_dhcp:
            self.network_force_dhcp_check.setChecked(bool(force_dhcp.get("Enable")))
        for check in self._disable_conn_checks.values():
            check.setEnabled(False)
            check.setChecked(False)
        self._network_disable_conn_config = {}
        if isinstance(disable_xm_server, dict) and "Ret" not in disable_xm_server:
            self._network_disable_conn_config = disable_xm_server
            for key, value in disable_xm_server.items():
                if key in ("Name", "Ret", "SessionID"):
                    continue
                check = self._disable_conn_checks.get(key)
                if check is None:
                    check = QCheckBox(key)
                    self.network_disable_conn_layout.insertWidget(
                        self.network_disable_conn_layout.count() - 1, check)
                    self._disable_conn_checks[key] = check
                if isinstance(value, str):
                    check.setChecked(value.strip().lower() in ("true", "1", "yes"))
                else:
                    check.setChecked(bool(value))
                check.setEnabled(True)
        if isinstance(ability, dict) and ability:
            self._network_ability_config = ability
            self.network_vnic_check.setChecked(bool(ability.get("VNICFunctionEnable")))
        if isinstance(oemcfg, dict) and oemcfg:
            self._network_oemcfg_config = oemcfg
            try:
                self.network_onvif_edit.setText(str(oemcfg.get("Port") or 8899))
            except (TypeError, ValueError):
                pass
        if isinstance(nat, dict) and nat:
            self._network_nat_config = nat
            self.nat_group.setChecked(bool(nat.get("NatEnable")))
            self.network_nat_addr_edit.setText(str(nat.get("Addr") or ""))
            self.network_nat_dns1_edit.setValue(format_ipv4(nat.get("DnsServer1")))
            self.network_nat_dns2_edit.setValue(format_ipv4(nat.get("DnsServer2")))
            self.network_nat_port_edit.setText(str(nat.get("Port") or 8000))
            self.network_nat_mtu_edit.setText(str(nat.get("XMeyeMTU") or 1280))
        if isinstance(wifi, dict) and wifi:
            self._network_wifi_config = wifi
            self.wifi_group.setChecked(bool(wifi.get("Enable")))
            self.network_wifi_ssid_edit.setCurrentText(str(wifi.get("SSID") or ""))
            self.network_wifi_password_edit.setText(str(wifi.get("Keys") or ""))
            auth = str(wifi.get("Auth") or "OPEN")
            if self.network_wifi_auth_combo.findText(auth) < 0:
                self.network_wifi_auth_combo.addItem(auth)
            self.network_wifi_auth_combo.setCurrentText(auth)
            encrypt = str(wifi.get("EncrypType") or "NONE")
            if self.network_wifi_encrypt_combo.findText(encrypt) < 0:
                self.network_wifi_encrypt_combo.addItem(encrypt)
            self.network_wifi_encrypt_combo.setCurrentText(encrypt)
            self.network_wifi_nettype_combo.setCurrentText(
                str(wifi.get("NetType") or "Infra"))
        for widget in (self.network_dns1_edit, self.network_dns2_edit,
                       self.network_default_dns_button, self.network_adaptive_check,
                       self.network_dhcp_check, self.network_smartnet_check,
                       self.network_smartnet_auto_check,
                       self.network_smartnet_change_ip_check):
            widget.setEnabled(True)

    def _selected_device(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return self.model.device_at(rows[0].row())

    def _select_device_identity(self, identity):
        for row in range(self.model.rowCount()):
            device = self.model.device_at(row)
            if device is not None and DeviceTableModel.identity(device) == identity:
                model = self.table.selectionModel()
                model.blockSignals(True)
                self.table.blockSignals(True)
                self.table.selectRow(row)
                self.table.blockSignals(False)
                model.blockSignals(False)
                return True
        return False

    def _on_table_selection(self, *_):
        device = self._selected_device()
        if device is None:
            return
        identity = DeviceTableModel.identity(device)
        if (self._connected_identity is not None
                and identity != self._connected_identity):
            if self._select_device_identity(self._connected_identity):
                return
        self.initial_ip_edit.setValue(next_ip_address(device.get("ip")))
        self._set_channel_count((device.get("raw") or {}).get("ChannelNum"))
        connected = (self._connected_identity is not None
                     and identity == self._connected_identity)
        if (connected and self._fetched_payload is not None
                and self._fetched_identity == identity):
            self._enable_device_tabs()
            self._on_system_fetched(self._fetched_payload, quiet=True)
        else:
            self._clear_device_tabs()
            self._disable_device_tabs()
            self._fill_broadcast_fields(device)
        self.save_button.setEnabled(True)

    def _on_model_layout_changed(self):
        QTimer.singleShot(0, self._sync_selection_state)

    def _sync_selection_state(self):
        device = self._selected_device()
        if device is None:
            self._disable_device_tabs()
            return
        identity = DeviceTableModel.identity(device)
        connected = (self._connected_identity is not None
                     and identity == self._connected_identity)
        if (self._connected_identity is not None and not connected):
            if self._select_device_identity(self._connected_identity):
                return
        if connected:
            self._enable_device_tabs()
        else:
            self._clear_device_tabs()
            self._disable_device_tabs()
            self._fill_broadcast_fields(device)
        self.save_button.setEnabled(True)

    def _device_tab_widgets(self):
        widgets = []
        for index in range(self.tabs.count()):
            panel = self.tabs.widget(index)
            if panel in (getattr(self, "_settings_scroll", None),
                         getattr(self, "_settings_panel", None)):
                continue
            for cls in (QLineEdit, QComboBox, QCheckBox, QSpinBox, QPushButton,
                        QTableWidget):
                widgets.extend(panel.findChildren(cls))
        widgets.extend((self.nat_group, self.ntp_group, self.upgrade_group,
                        self.wifi_group))
        return widgets

    def _update_upgrade_controls(self, *_):
        """Keep the local firmware picker (and Upgrade when connected) usable.

        The Upgrade group is checkable, so Qt disables its children whenever
        the device reports the online-upgrade feature as disabled; the file
        edit's internal icon button has to be re-enabled explicitly.
        """
        self.network_upgrade_file_edit.setEnabled(True)
        for child in self.network_upgrade_file_edit.findChildren(QWidget):
            child.setEnabled(True)
        if self._connected_identity is not None:
            self.network_upgrade_button.setEnabled(True)

    def _enable_device_tabs(self):
        for widget in self._device_tab_widgets():
            widget.setEnabled(True)
        for key, check in self._disable_conn_checks.items():
            check.setEnabled(key in self._network_disable_conn_config)
        self._update_upgrade_controls()
        self._update_channels_button()
        self._update_encode_table_button()

    def _disable_device_tabs(self):
        for widget in self._device_tab_widgets():
            if widget is self.upgrade_group:
                continue
            widget.setEnabled(False)
        for child in self.upgrade_group.findChildren(QWidget):
            if child is self.network_upgrade_file_edit:
                continue
            if self.network_upgrade_file_edit.isAncestorOf(child):
                continue
            child.setEnabled(False)
        self._update_upgrade_controls()
        self.network_default_ip_button.setEnabled(True)
        self.network_default_dns_button.setEnabled(True)
        self.system_recovery_button.setEnabled(True)
        self.system_dump_button.setEnabled(True)
        self.system_open_dir_button.setEnabled(True)
        self.encode_summary_group.setVisible(False)
        self._update_cloud_qr("")

    def _refresh_age_label(self):
        widget = getattr(self, "system_age_edit", None)
        if widget is None:
            return
        if self._age_runtime is not None:
            minutes, fetched = self._age_runtime
            minutes += int((time.time() - fetched) // 60)
            text = format_device_runtime(minutes)
            if text:
                widget.setText(text)
                return
        if self._age_build_time:
            widget.setText(format_device_age(self._age_build_time))

    def _clear_device_tabs(self):
        self._age_build_time = None
        self._age_runtime = None
        for index in range(self.tabs.count()):
            panel = self.tabs.widget(index)
            if panel in (getattr(self, "_settings_scroll", None),
                         getattr(self, "_settings_panel", None)):
                continue
            for widget in panel.findChildren(QWidget):
                widget.blockSignals(True)
            for widget in panel.findChildren(QLineEdit):
                if widget is self.network_upgrade_file_edit:
                    continue
                widget.clear()
            for widget in panel.findChildren(QComboBox):
                widget.setCurrentIndex(-1)
            for widget in panel.findChildren(QCheckBox):
                widget.setChecked(False)
            for widget in panel.findChildren(QSpinBox):
                widget.setValue(widget.minimum())
            for widget in panel.findChildren(QTableWidget):
                widget.setRowCount(0)
            for widget in panel.findChildren(QWidget):
                widget.blockSignals(False)
        self.encode_summary_group.setVisible(False)
        self._update_cloud_qr("")

    @staticmethod
    def _device_type_name(value):
        try:
            number = int(value)
        except (TypeError, ValueError):
            return "" if value is None else str(value)
        return DigitalChannelsDialog.DEVICE_TYPES.get(number, str(number))

    def _update_cloud_qr(self, text=None):
        label = getattr(self, "system_qr_label", None)
        if label is None:
            return
        cloud = str(text if text is not None
                    else self.system_cloud_edit.text()).strip()
        if not cloud or qrcode is None:
            label.clear()
            label.setVisible(False)
            return
        try:
            code = qrcode.QRCode(
                border=2,
                error_correction=qrcode.constants.ERROR_CORRECT_M)
            code.add_data(cloud)
            code.make(fit=True)
            matrix = code.get_matrix()
        except Exception:
            label.clear()
            label.setVisible(False)
            return
        modules = len(matrix)
        scale = max(2, 190 // modules)
        size = modules * scale
        image = QImage(size, size, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.white)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(Qt.GlobalColor.black)
        for y, row in enumerate(matrix):
            for x, dark in enumerate(row):
                if dark:
                    painter.drawRect(x * scale, y * scale, scale, scale)
        painter.end()
        label.setPixmap(QPixmap.fromImage(image))
        label.setToolTip("Cloud ID: %s" % cloud)
        label.setVisible(True)

    def _fill_broadcast_fields(self, device):
        if not isinstance(device, dict):
            return
        raw = device.get("raw") or {}
        enabled = []
        name = str(raw.get("HostName") or device.get("host_name") or "")
        if name:
            self.network_name_edit.setText(name)
            enabled.append(self.network_name_edit)
        ip = device.get("ip")
        if ip:
            self.network_address_edit.setValue(ip)
            enabled.append(self.network_address_edit)
        subnet = device.get("subnet")
        if subnet:
            self.network_submask_edit.setValue(subnet)
            enabled.append(self.network_submask_edit)
        gateway = device.get("gateway")
        if gateway:
            self.network_gateway_edit.setValue(gateway)
            enabled.append(self.network_gateway_edit)
        http_port = device.get("http_port") or raw.get("HttpPort")
        if http_port:
            self.network_http_edit.setText(str(http_port))
            enabled.append(self.network_http_edit)
        tcp_port = device.get("tcp_port") or raw.get("TCPPort")
        if tcp_port:
            self.network_tcp_edit.setText(str(tcp_port))
            enabled.append(self.network_tcp_edit)
        transfer = str(raw.get("TransferPlan") or "")
        if transfer:
            if self.network_transfer_combo.findText(transfer) < 0:
                self.network_transfer_combo.addItem(transfer)
            self.network_transfer_combo.setCurrentText(transfer)
            enabled.append(self.network_transfer_combo)
        if "UseHSDownLoad" in raw:
            self.network_hsdownload_check.setChecked(bool(raw.get("UseHSDownLoad")))
            enabled.append(self.network_hsdownload_check)
        if name:
            self.system_hardware_edit.setText(name)
            enabled.append(self.system_hardware_edit)
        version = str(device.get("version") or "")
        if version:
            self.system_software_edit.setText(version)
            enabled.append(self.system_software_edit)
        cloud = str(device.get("cloud_id") or device.get("sn") or "")
        if cloud:
            self.system_cloud_edit.setText(cloud)
            enabled.append(self.system_cloud_edit)
        build = normalize_build_time(device.get("build_date"))
        if build:
            self.system_build_edit.setText(build)
            enabled.append(self.system_build_edit)
            self._age_build_time = build
            self._age_runtime = None
            self.system_age_edit.setText(format_device_age(build))
            enabled.append(self.system_age_edit)
        channels = raw.get("ChannelNum")
        if channels is not None:
            self.system_channels_edit.setText(str(channels))
            enabled.append(self.system_channels_edit)
        device_type = device.get("device_type")
        if device_type is None:
            device_type = raw.get("DeviceType")
        if device_type is not None:
            self.system_type_edit.setText(self._device_type_name(device_type))
            enabled.append(self.system_type_edit)
        for widget in enabled:
            widget.setEnabled(True)
            for child in widget.findChildren(QWidget):
                child.setEnabled(True)

    def _system_target(self):
        return self._target_device()

    def _device_credentials(self, device):
        username = device.get("username") or self.user_edit.text().strip() or "admin"
        password = device.get("password")
        if password is None:
            password = self.password_edit.text()
        return username, password

    def _device_by_identity(self, identity):
        if identity is None:
            return None
        for device in self.model.devices():
            if DeviceTableModel.identity(device) == identity:
                return device
        return None

    def _set_connection_text(self, source):
        self.connection_label.setProperty("_i18n_label_source", source)
        self.connection_label.setProperty("_i18n_label_last", tr(source))
        self.connection_label.setText(tr(source))

    def _drop_connection(self, message=""):
        identity = self._connected_identity
        if identity is None:
            return
        self._stop_session()
        self.model.set_connected(identity, False)
        self._connected_identity = None
        self._connect_pending = None
        self._fetched_payload = None
        self._fetched_identity = None
        self._fetched_keys = set()
        self._pending_fetch_keys = set()
        self._set_connection_text("Disconnected")
        self._sync_selection_state()
        if message:
            self._message(message)

    def _disconnect_device(self):
        self._drop_connection("Disconnected")

    def _start_session(self, device):
        """Keep a real NETIP socket open so a dropped connection is noticed."""
        self._stop_session()
        if not isinstance(device, dict):
            return
        username, password = self._device_credentials(device)
        thread = NetipSessionThread(
            device.get("ip") or "", username, password,
            cloud_id=device.get("cloud_id") or "",
            rps=bool(device.get("rps", True)),
            port=int(device.get("tcp_port") or 34567),
            no_md5=bool(device.get("no_md5")),
            parent=self)
        thread.lost.connect(self._on_session_lost)
        thread.finished.connect(thread.deleteLater)
        self._session_thread = thread
        thread.start()

    def _stop_session(self):
        thread = self._session_thread
        self._session_thread = None
        if thread is not None:
            thread.stop()
            if not thread.wait(2000):
                thread.finished.connect(thread.deleteLater)

    def _on_session_lost(self, text):
        if self._connected_identity is None:
            return
        device = self._device_by_identity(self._connected_identity)
        label = (device.get("ip") if isinstance(device, dict) else "") \
            or self._connected_identity
        if self.video_panel.is_active():
            self._stop_video()
        self._drop_connection("Connection lost: %s" % label)

    def _on_video_lost(self, text):
        if self.video_panel.is_active():
            self._stop_video()
        if self._connected_identity is not None:
            self._drop_connection("Connection lost")

    def _connect_device(self, index):
        device = self.model.device_at(index.row())
        if device is None:
            return
        identity = DeviceTableModel.identity(device)
        if self._connected_identity == identity:
            self._disconnect_device()
            return
        previous = self._connected_identity
        if previous is not None and previous != identity:
            self.model.set_connected(previous, False)
        self._connected_identity = identity
        self.model.set_connected(identity, True)
        self._fetched_keys = set()
        self._fetched_payload = None
        self._fetched_identity = None
        self._pending_fetch_keys = set()
        self.table.selectRow(index.row())
        self.initial_ip_edit.setValue(device.get("ip") or "")
        self._fill_network_fields(device)
        self._connect_pending = identity
        self._start_session(device)
        label = "Switching to" if previous is not None and previous != identity else "Connecting to"
        keys = sorted(set(self._tab_fetch_keys(self.tabs.currentIndex()))
                      | {"system", "common"})
        self._start_system_action(
            "fetch", device=device, label=label, changes={"keys": keys})

    def _tab_fetch_keys(self, index):
        if not (0 <= index < self.tabs.count()):
            return []
        name = self.tabs.tabText(index)
        for tab_name, keys in TAB_FETCH_KEYS:
            if tab_name == name:
                return list(keys)
        return []

    def _request_fetch(self, keys):
        if self._connected_identity is None:
            return
        keys = [key for key in keys if key not in self._fetched_keys]
        if not keys:
            return
        if self._netip_thread is not None:
            self._pending_fetch_keys.update(keys)
            return
        device = self._system_target()
        if not isinstance(device, dict):
            return
        self._pending_fetch_keys = set()
        self._start_system_action(
            "fetch", device=device, label="Fetching",
            changes={"keys": keys})

    def _on_tab_changed(self, index):
        if self._connected_identity is None:
            return
        keys = self._tab_fetch_keys(index)
        missing = [key for key in keys if key not in self._fetched_keys]
        if missing:
            self._request_fetch(missing)
        elif self._fetched_payload:
            self._on_system_fetched({}, quiet=True)

    def _on_system_connected(self, name, thread=None):
        if thread is not None and thread is not self._netip_thread:
            return
        self._set_connection_text("Connected: %s" % name)
        if self._connect_pending is not None:
            self.model.set_connected(self._connect_pending, True)
            self._connect_pending = None
        self._update_upgrade_controls()

    def _on_system_progress(self, text):
        self.fetch_label.setText(tr(text))

    @staticmethod
    def _save_setting(key, value):
        settings = QSettings("xmdm3", "xmdms")
        settings.setValue(key, value)
        settings.sync()

    def _theme_changed(self, *_):
        code = str(self.settings_theme_combo.currentData() or "auto")
        self._save_setting("theme", code)
        apply_theme(QApplication.instance(), code)

    def _passwords_changed(self, *_):
        visible = bool(self.settings_passwords_combo.currentData())
        self._save_setting("show_passwords", visible)
        apply_password_visibility(visible)

    def _on_settings_tab(self, index):
        if (index == self.tabs.indexOf(self._settings_scroll)
                and not self._updates_checked):
            self._updates_checked = True
            self._check_updates()

    def _check_updates(self):
        if self._release_thread is not None:
            return
        self._set_about_state("checking")
        self.about_check_button.setEnabled(False)
        thread = ReleaseCheckThread(self)
        thread.result.connect(self._on_update_result)
        thread.error.connect(self._on_update_error)
        thread.finished.connect(self._release_finished)
        thread.finished.connect(thread.deleteLater)
        self._release_thread = thread
        thread.start()

    def _release_finished(self):
        self._release_thread = None
        self.about_check_button.setEnabled(True)

    def _set_about_state(self, kind, payload=None):
        self._about_state = (kind, payload)
        self._render_about_state()

    def _render_about_state(self):
        kind, payload = self._about_state
        if kind == "checking":
            self.about_status_label.setText(tr("Checking for updates..."))
        elif kind == "error":
            self.about_status_label.setText(
                tr("Update check failed: ") + tr(payload))
        elif kind == "result":
            self._render_update_result(payload)
        else:
            self.about_status_label.setText(tr("Not checked"))

    def _on_update_error(self, text):
        self._set_about_state("error", text)

    def _on_update_result(self, data):
        self._set_about_state("result", data)

    def _render_update_result(self, data):
        kind = data.get("kind") if isinstance(data, dict) else None
        if kind == "release":
            tag = str(data.get("tag") or "")
            title = str(data.get("name") or tag)
            if version_key(tag) > version_key(APP_VERSION):
                status = "%s %s (%s %s)" % (
                    tr("Update available:"), tag,
                    tr("current"), APP_VERSION)
            else:
                status = "%s %s" % (tr("Up to date — latest"), tag)
            self.about_status_label.setText(status)
            body = str(data.get("body") or "").strip()
            if not body:
                body = tr("No release notes.")
            markdown = "## %s\n\n%s" % (title, body)
            date = format_date(data.get("date"))
            if date:
                markdown += "\n\n_%s_" % date
            self.about_notes.setMarkdown(markdown)
            url = str(data.get("url") or "")
            self.about_notes.setToolTip(url)
        elif kind == "commit":
            sha = str(data.get("sha") or "")
            short = sha[:7]
            branch = str(data.get("branch") or "main")
            if BUILD_COMMIT and sha.lower().startswith(
                    BUILD_COMMIT.lower()):
                status = "%s %s" % (tr("Up to date — latest commit"), short)
            elif BUILD_COMMIT and remote_is_newer(
                    data.get("date"), BUILD_TIMESTAMP or BUILD_DATE):
                status = "%s %s (%s)" % (
                    tr("New commits available on"), branch, short)
            elif BUILD_COMMIT:
                status = "%s %s" % (tr("Up to date — latest commit"), short)
            else:
                status = "%s %s" % (tr("Latest commit:"), short or "?")
            self.about_status_label.setText(status)
            message = str(data.get("message") or "").strip()
            if not message:
                message = tr("No commit message.")
            details = "%s\n\n%s" % (short, message)
            date = format_date(data.get("date"))
            if date:
                details += "\n%s" % date
            self.about_notes.setPlainText(details)
            url = str(data.get("url") or "")
            self.about_notes.setToolTip(url)

    def _language_changed(self, *_):
        setting = str(self.settings_language_combo.currentData() or "auto")
        self._save_setting("language", setting)
        set_language(resolve_language(setting))
        retranslate_windows()
        self.about_notes.setPlaceholderText(tr("No release notes."))
        self._render_about_state()
        self._update_language_combo_labels()
        self._fit_system_buttons()
        self.model.headerDataChanged.emit(
            Qt.Orientation.Horizontal, 0, self.model.columnCount() - 1)
        self.status_label.setText(self._refresh_status_text())

    def _update_language_combo_labels(self):
        theme = {"auto": tr("Auto"), "light": tr("Light"), "dark": tr("Dark")}
        for index in range(self.settings_theme_combo.count()):
            code = self.settings_theme_combo.itemData(index)
            if code in theme:
                self.settings_theme_combo.setItemText(index, theme[code])
        passwords = {True: tr("Show"), False: tr("Hide")}
        for index in range(self.settings_passwords_combo.count()):
            code = bool(self.settings_passwords_combo.itemData(index))
            if code in passwords:
                self.settings_passwords_combo.setItemText(
                    index, passwords[code])
        labels = {"auto": tr("Auto"), "en": tr("English"),
                  "ru": tr("Russian")}
        for index in range(self.settings_language_combo.count()):
            code = self.settings_language_combo.itemData(index)
            if code in labels:
                self.settings_language_combo.setItemText(index, labels[code])

    def _fit_system_buttons(self):
        buttons = (
            self.system_import_button, self.system_export_button,
            self.system_reset_button, self.system_logs_button,
            self.system_erase_logs_button, self.system_recovery_button,
            self.system_dump_button, self.system_open_dir_button)
        width = max(84, max(button.sizeHint().width()
                            for button in buttons) + 10)
        for button in buttons:
            button.setMinimumWidth(width)
            button.setMaximumWidth(width)
        grid = getattr(self, "system_buttons_grid", None)
        if grid is not None:
            for index in range(grid.count()):
                widget = grid.itemAt(index).widget()
                if isinstance(widget, QPushButton):
                    widget.setMinimumWidth(width)
                    widget.setMaximumWidth(width)
            grid.setColumnMinimumWidth(0, width)
            grid.invalidate()

    def _save_current_tab(self):
        index = self.tabs.currentIndex()
        if index == 0:
            self._apply_network()
        elif index == 1:
            self._system_apply()
        elif index == 2:
            self._display_apply()
        elif index == 3:
            self._encode_apply()
        elif index == 4:
            self._camera_apply()
        elif index == 5:
            self._storage_refresh()
        elif index == 6:
            self._serial_ptz_apply()
        elif index == 7:
            self._users_refresh()
        else:
            self._message("Settings are applied to new searches automatically.")

    def _open_console(self):
        bus = query_log_bus()
        if bus is None:
            install_query_logger()
            bus = query_log_bus()
        if self._console_dialog is None:
            self._console_dialog = QueryConsoleDialog(bus, parent=self)
        self._console_dialog.show()
        self._console_dialog.raise_()
        self._console_dialog.activateWindow()

    def _set_system_busy(self, busy):
        for widget in (self.system_sync_button, self.system_channels_button,
                       self.system_reboot_button, self.system_import_button,
                       self.system_export_button, self.system_reset_button,
                       self.system_logs_button, self.system_erase_logs_button):
            widget.setEnabled(not busy)
        if not busy:
            self._update_channels_button()

    def _update_channels_button(self):
        button = getattr(self, "system_channels_button", None)
        if button is None:
            return
        button.setEnabled(
            self._connected_identity is not None
            and self._channel_count > 1
            and self._netip_thread is None)

    def _start_system_action(self, action, changes=None, label="", device=None,
                             on_fetched=None, on_applied=None):
        if self._netip_thread is not None:
            if action != "fetch":
                self._message("NetIP operation already running.")
                return
            previous = self._netip_thread
            previous.cancel()
            self._stale_threads.append(previous)
            self._netip_thread = None
        if device is None:
            device = self._system_target()
        if not isinstance(device, dict):
            self._message("No device selected — pick a table row first.")
            return
        username, password = self._device_credentials(device)
        thread = NetipThread(
            action, device.get("ip") or "",
            username, password,
            cloud_id=device.get("cloud_id") or "",
            rps=bool(device.get("rps", True)),
            changes=changes,
            port=device.get("tcp_port") or 34567,
            parent=self,
            no_md5=bool(device.get("no_md5")))
        thread.fetched.connect(on_fetched or self._on_system_fetched)
        thread.applied.connect(on_applied or self._on_system_applied)
        thread.failed.connect(lambda text, t=thread: self._on_system_failed(text, t))
        thread.progress.connect(self._on_system_progress)
        thread.connected.connect(
            lambda name, t=thread: self._on_system_connected(name, t))
        thread.finished.connect(lambda t=thread: self._on_system_finished(t))
        self._netip_thread = thread
        self._fetch_in_progress = action == "fetch"
        self._system_error = False
        self._set_system_busy(True)
        self._message("%s %s ..." % (label or action, device.get("ip") or ""))
        thread.start()

    def _system_apply(self):
        if self._system_payload is None:
            self._message("Fetch device data first.")
            return
        values = {
            "tv_standard": self.system_tv_combo.currentText().strip(),
            "language": self.system_language_combo.currentText().strip(),
            "date_format": self.system_date_combo.currentText().strip(),
            "separator": self.system_separator_combo.currentText().strip(),
            "time_format": "12" if self.system_hour_combo.currentIndex() == 1 else "24",
        }
        maintain = {}
        day = self.system_restart_day_combo.currentText()
        if day:
            maintain = {
                "AutoRebootDay": day,
                "AutoRebootHour": int(self.system_restart_hour_combo.currentData() or 0),
            }
        preview_num = self.system_maxchannels_combo.currentData()
        timezone = {}
        if self._system_timezone_config:
            config = dict(self._system_timezone_config)
            offset = self.system_timezone_combo.currentData()
            if offset is not None:
                config["timeMin"] = -int(offset)
            timezone = config
        device_desc = {}
        if self._system_device_desc_config:
            desc = dict(self._system_device_desc_config)
            try:
                beep = int(str(desc.get("EnableBeep") or "0"), 0)
            except (TypeError, ValueError):
                beep = 0
            if self.system_beeper_check.isChecked():
                beep |= 1
            else:
                beep &= ~1
            desc["EnableBeep"] = "0x%08X" % (beep & 0xFFFFFFFF)
            desc["EnableDebugMode"] = self.display_debug_check.isChecked()
            device_desc = desc
        ability = dict(self._network_ability_config)
        if ability:
            ability["FaceFunctionEnable"] = self.display_face_check.isChecked()
            self._network_ability_config = ability
        changes = {"values": values, "keys": dict(self._system_general_keys),
                   "maintain": maintain,
                   "timezone": timezone,
                   "device_desc": device_desc,
                   "preview_num": preview_num}
        if ability:
            changes["ability"] = ability
        self._start_system_action("apply", changes=changes, label="Applying")

    def _display_apply(self):
        video_out = {}
        if self._display_video_out_config:
            config = dict(self._display_video_out_config)
            base = self.display_resolution_combo.currentText().split("(")[0]
            parts = base.strip().replace("*", "x").split("x")
            if len(parts) == 2:
                try:
                    width, height = int(parts[0]), int(parts[1])
                except ValueError:
                    width = height = None
                if width and height:
                    config["Mode"] = {"Width": width, "Height": height}
            video_out = config
        gui_set = {}
        if self._display_gui_set_config:
            config = dict(self._display_gui_set_config)
            for key, check in self._display_gui_checks.items():
                config[key] = check.isChecked()
            config["WindowAlpha"] = int(self.display_window_alpha_spin.value())
            gui_set = config
        ability = dict(self._network_ability_config)
        ability["FaceFunctionEnable"] = self.display_face_check.isChecked()
        self._network_ability_config = ability
        device_desc = {}
        if self._system_device_desc_config:
            desc = dict(self._system_device_desc_config)
            desc["EnableDebugMode"] = self.display_debug_check.isChecked()
            device_desc = desc
        self._start_system_action(
            "apply",
            changes={"video_out": video_out, "gui_set": gui_set,
                     "ability": ability, "device_desc": device_desc},
            label="Applying display settings on")

    @staticmethod
    def _normalize_av_enc(reply):
        if isinstance(reply, list):
            return reply, [item for item in reply if isinstance(item, dict)]
        if isinstance(reply, dict):
            encode = reply.get("Encode")
            if isinstance(encode, list):
                return reply, [item for item in encode if isinstance(item, dict)]
            main = reply.get("MainFormat")
            extra = reply.get("ExtraFormat")
            if isinstance(main, list):
                entries = []
                for index, item in enumerate(main):
                    if not isinstance(item, dict):
                        continue
                    entry = {"MainFormat": item}
                    if (isinstance(extra, list) and index < len(extra)
                            and isinstance(extra[index], dict)):
                        entry["ExtraFormat"] = extra[index]
                    entries.append(entry)
                return reply, entries
        return None, []

    def _build_encode_fields(self):
        for prefix in ("main", "sub"):
            fields = {}
            codec = QComboBox()
            codec.addItems(ENCODE_CODECS)
            fields["codec"] = codec
            resolution = QComboBox()
            resolution.addItems(ENCODE_RESOLUTIONS)
            fields["res"] = resolution
            fps = QSpinBox()
            fps.setRange(1, 30)
            fields["fps"] = fps
            rate = QComboBox()
            rate.addItems(ENCODE_RATE_CONTROL)
            fields["rc"] = rate
            quality = QSpinBox()
            quality.setRange(1, 6)
            fields["quality"] = quality
            bitrate = QSpinBox()
            bitrate.setRange(0, 65535)
            bitrate.setSuffix(" kbps")
            fields["bitrate"] = bitrate
            gop = QSpinBox()
            gop.setRange(1, 250)
            fields["gop"] = gop
            video = QCheckBox("Video")
            fields["video"] = video
            audio = QCheckBox("Audio")
            fields["audio"] = audio
            smart = QComboBox()
            fields["smart"] = smart
            self.encode_widgets[prefix] = fields

            def refresh(*_, prefix=prefix):
                self._encode_update_bitrate(prefix)

            for key in ("codec", "res", "rc"):
                fields[key].currentTextChanged.connect(refresh)
            fields["res"].currentTextChanged.connect(
                self._encode_resolution_changed)
            for key in ("quality", "fps", "gop"):
                fields[key].valueChanged.connect(refresh)

    def _encode_update_bitrate(self, prefix):
        if self._encode_current is None:
            return
        entry = self._encode_entry(self._encode_current)
        if not isinstance(entry, dict):
            return
        fields = self.encode_widgets[prefix]
        vbr = fields["rc"].currentText().strip().upper() == "VBR"
        fields["quality"].setEnabled(vbr)
        fields["bitrate"].setEnabled(not vbr)
        if not vbr:
            return
        value = encode_vbr_bitrate(
            fields["res"].currentText(), fields["codec"].currentText(),
            fields["quality"].value(), fields["fps"].value(),
            fields["gop"].value(), self._encode_max_fps)
        if value is None:
            return
        value = min(value, fields["bitrate"].maximum())
        if value != fields["bitrate"].value():
            fields["bitrate"].blockSignals(True)
            fields["bitrate"].setValue(value)
            fields["bitrate"].blockSignals(False)

    def _encode_entry(self, chn):
        if chn is None:
            return None
        if self._encode_mode == "nvr":
            if 0 <= chn < len(self._encode_configs):
                config = self._encode_configs[chn]
                if isinstance(config, list) and config and isinstance(config[0], dict):
                    return config[0]
        elif self._encode_mode == "av":
            if 0 <= chn < len(self._encode_av_entries):
                entry = self._encode_av_entries[chn]
                if isinstance(entry, dict):
                    return entry
        return None

    def _encode_smart_state(self, chn):
        if chn is None:
            return None
        if 0 <= chn < len(self._encode_smart):
            state = self._encode_smart[chn]
            if isinstance(state, dict):
                return state
        return None

    def _encode_set_stream(self, prefix, fmt, smart_state, index):
        fields = self.encode_widgets[prefix]
        video = fmt.get("Video") if isinstance(fmt.get("Video"), dict) else {}
        fields["codec"].setCurrentText(str(video.get("Compression") or ""))
        fields["res"].setCurrentText(str(video.get("Resolution") or ""))
        for key, default, minimum, maximum in (
                ("fps", 1, 1, 30), ("quality", 1, 1, 6),
                ("bitrate", 0, 0, 65535), ("gop", 1, 1, 250)):
            try:
                value = int(video.get({"fps": "FPS", "quality": "Quality",
                                       "bitrate": "BitRate",
                                       "gop": "GOP"}[key]))
            except (TypeError, ValueError):
                value = default
            fields[key].setValue(value if minimum <= value <= maximum else default)
        fields["rc"].setCurrentText(str(video.get("BitRateControl") or ""))
        fields["video"].setChecked(bool(fmt.get("VideoEnable")))
        fields["audio"].setChecked(bool(fmt.get("AudioEnable")))
        mode = smart_state.get("mode") if smart_state else None
        smart_combo = fields["smart"]
        smart_combo.blockSignals(True)
        smart_combo.clear()
        if mode == "v2":
            smart_combo.addItems(["Off", "H265+", "H265AI"])
        elif mode == "v1":
            smart_combo.addItems(["Off", "H265+"])
        else:
            smart_combo.addItem("Off")
        value = "Off"
        if smart_state:
            config = smart_state.get("config") or {}
            if mode == "v2":
                plus = config.get("Smart264PlusV2")
                entries = config.get("Smart264V2")
                plus_on = (isinstance(plus, list) and index < len(plus)
                           and isinstance(plus[index], dict)
                           and plus[index].get("SmartH264Plus") == 1)
                v2_on = (isinstance(entries, list) and index < len(entries)
                         and isinstance(entries[index], dict)
                         and entries[index].get("SmartH264"))
                value = "H265AI" if plus_on else "H265+" if v2_on else "Off"
            elif mode == "v1" and config.get("SmartH264"):
                value = "H265+"
        smart_combo.setCurrentText(value)
        smart_combo.blockSignals(False)
        for widget in fields.values():
            widget.setEnabled(True)
        smart_combo.setEnabled(mode is not None)

    def _encode_load_channel(self, chn):
        self._encode_current = chn
        entry = self._encode_entry(chn)
        smart_state = self._encode_smart_state(chn)
        if not isinstance(entry, dict):
            for fields in self.encode_widgets.values():
                for widget in fields.values():
                    widget.setEnabled(False)
            return
        main = entry.get("MainFormat") if isinstance(entry.get("MainFormat"), dict) else {}
        extra = entry.get("ExtraFormat") if isinstance(entry.get("ExtraFormat"), dict) else {}
        main_video = main.get("Video") if isinstance(main.get("Video"), dict) else {}
        extra_video = extra.get("Video") if isinstance(extra.get("Video"), dict) else {}
        main_names, sub_names = self._encode_resolution_choices(chn)
        self._encode_set_resolution_items(
            "main", main_names, str(main_video.get("Resolution") or ""))
        self._encode_set_resolution_items(
            "sub", sub_names, str(extra_video.get("Resolution") or ""))
        self._encode_set_stream("main", main, smart_state, 0)
        self._encode_set_stream("sub", extra, smart_state, 1)
        self._encode_update_bitrate("main")
        self._encode_update_bitrate("sub")

    @staticmethod
    def _mask_resolution_names(mask):
        try:
            value = int(str(mask), 0)
        except (TypeError, ValueError):
            return []
        return [name for bit, name in enumerate(ENCODE_RESOLUTION_BITS)
                if value & (1 << bit)]

    @staticmethod
    def _resolution_bit_index(name):
        name = str(name or "").strip().upper()
        name = ENCODE_RESOLUTION_ALIASES.get(name, name)
        try:
            return ENCODE_RESOLUTION_BITS.index(name)
        except ValueError:
            return -1

    @staticmethod
    def _stream_resolution_mask(entries, stream_types):
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if str(entry.get("StreamType") or "") in stream_types:
                return entry.get("ResolutionMask")
        return None

    def _av_resolution_choices(self, ability):
        info = ability.get("EncodeInfo")
        if not isinstance(info, list):
            info = ability.get("CompEncodeInfo")
        if not isinstance(info, list):
            return [], []
        main_names = self._mask_resolution_names(
            self._stream_resolution_mask(info, ("MainStream",)))
        sub_names = self._mask_resolution_names(
            self._stream_resolution_mask(
                info, ("ExtraStream", "ExtraStream2", "SubStream")))
        return main_names, sub_names

    def _encode_resolution_choices(self, chn):
        if not (0 <= chn < len(self._encode_ability)):
            return [], []
        ability = self._encode_ability[chn]
        if not isinstance(ability, dict):
            return [], []
        if self._encode_mode == "av":
            return self._av_resolution_choices(ability)
        info = ability.get("ability") if isinstance(ability.get("ability"), dict) else ability
        main_names = []
        sizes = info.get("ImageSizePerChannel")
        if isinstance(sizes, list) and sizes:
            main_names = self._mask_resolution_names(sizes[0])
        sub_names = []
        ex = info.get("ExImageSizePerChannelEx")
        entry = self._encode_entry(chn)
        main_res = ""
        if isinstance(entry, dict):
            main_format = entry.get("MainFormat") if isinstance(entry.get("MainFormat"), dict) else {}
            video = main_format.get("Video") if isinstance(main_format.get("Video"), dict) else {}
            main_res = str(video.get("Resolution") or "")
        index = self._resolution_bit_index(main_res)
        if isinstance(ex, list) and ex and isinstance(ex[0], list) and 0 <= index < len(ex[0]):
            sub_names = self._mask_resolution_names(ex[0][index])
        return main_names, sub_names

    def _encode_set_resolution_items(self, prefix, names, current=""):
        combo = self.encode_widgets[prefix]["res"]
        combo.blockSignals(True)
        combo.clear()
        if names:
            combo.addItems(names)
        else:
            combo.addItems(ENCODE_RESOLUTIONS)
        if current and combo.findText(current) < 0:
            combo.addItem(current)
        combo.setCurrentText(current)
        combo.blockSignals(False)

    def _encode_channel_changed(self, *_):
        self._encode_store_current()
        self._encode_load_channel(self.encode_channel_combo.currentData())
        self._refresh_encode_summary()

    def _encode_store_current(self):
        chn = self._encode_current
        if chn is None:
            return
        entry = self._encode_entry(chn)
        if not isinstance(entry, dict):
            return
        self._write_encode_widgets(entry, self.encode_widgets, self._encode_smart_state(chn))

    def _write_encode_widgets(self, entry, widgets, smart_state):
        for prefix, format_key in (("main", "MainFormat"), ("sub", "ExtraFormat")):
            fields = widgets[prefix]
            fmt = entry.setdefault(format_key, {})
            if not isinstance(fmt, dict):
                fmt = {}
                entry[format_key] = fmt
            video = fmt.setdefault("Video", {})
            video["Compression"] = fields["codec"].currentText().strip()
            video["Resolution"] = fields["res"].currentText().strip()
            video["FPS"] = fields["fps"].value()
            video["BitRateControl"] = fields["rc"].currentText().strip()
            video["Quality"] = fields["quality"].value()
            video["BitRate"] = fields["bitrate"].value()
            video["GOP"] = fields["gop"].value()
            fmt["VideoEnable"] = fields["video"].isChecked()
            fmt["AudioEnable"] = fields["audio"].isChecked()
            if not smart_state:
                continue
            config = smart_state.get("config")
            if not isinstance(config, dict):
                continue
            mode = smart_state.get("mode")
            index = 0 if prefix == "main" else 1
            value = fields["smart"].currentText()
            if mode == "v2":
                plus = config.setdefault("Smart264PlusV2", [])
                smart = config.setdefault("Smart264V2", [])
                while len(plus) <= index:
                    plus.append({})
                while len(smart) <= index:
                    smart.append({})
                if isinstance(plus[index], dict):
                    plus[index]["SmartH264Plus"] = 1 if value == "H265AI" else 0
                if isinstance(smart[index], dict):
                    smart[index]["SmartH264"] = value == "H265+"
            elif mode == "v1" and prefix == "main":
                config["SmartH264"] = value != "Off"

    def _fill_encode_tab(self, payload):
        general = payload.get("general") if isinstance(payload.get("general"), dict) else {}
        location = general.get("Location") if isinstance(general.get("Location"), dict) else {}
        video_format = str(location.get("VideoFormat") or general.get("VideoStandard") or "")
        self._encode_max_fps = 30 if video_format.strip().upper().startswith("NTSC") else 25
        ability = payload.get("encode_ability")
        self._encode_ability = ability if isinstance(ability, list) else []
        configs = payload.get("encode_channels")
        av_encode = payload.get("av_encode")
        smart = payload.get("encode_smart")
        self._encode_smart = smart if isinstance(smart, list) else []
        status = payload.get("chn_status")
        self._encode_channel_names = []
        if isinstance(status, list):
            for item in status:
                self._encode_channel_names.append(
                    str(item.get("ChnName") or "").strip()
                    if isinstance(item, dict) else "")
        if isinstance(configs, list) and configs:
            self._encode_mode = "nvr"
            self._encode_configs = configs
            self._encode_av_enc = None
            self._encode_av_entries = []
            entries = []
            for config in configs:
                if (isinstance(config, list) and config
                        and isinstance(config[0], dict)):
                    entries.append(config[0])
                else:
                    entries.append(None)
        elif isinstance(av_encode, (list, dict)):
            self._encode_mode = "av"
            self._encode_configs = []
            self._encode_av_enc, self._encode_av_entries = self._normalize_av_enc(av_encode)
            if self._encode_av_enc is None:
                self._encode_mode = None
                entries = []
            else:
                entries = list(self._encode_av_entries)
        else:
            self._encode_mode = None
            self._encode_configs = []
            self._encode_av_enc = None
            self._encode_av_entries = []
            entries = []
        combo = self.encode_channel_combo
        combo.blockSignals(True)
        combo.clear()
        for chn in range(len(entries)):
            combo.addItem("CAM%02d" % (chn + 1), chn)
        target = 0
        for chn, entry in enumerate(entries):
            if isinstance(entry, dict):
                target = chn
                break
        combo.setCurrentIndex(target if entries else -1)
        combo.blockSignals(False)
        self._encode_current = None
        if entries:
            self._encode_load_channel(combo.currentData())
        else:
            self._encode_load_channel(None)
        self._refresh_encode_summary()
        self._update_encode_table_button()

    def _encode_smart_changes(self):
        changes = []
        for chn, state in enumerate(self._encode_smart):
            if not isinstance(state, dict):
                continue
            config = state.get("config")
            if not isinstance(config, dict):
                continue
            mode = state.get("mode")
            if mode in ("v1", "v2"):
                changes.append((chn, mode, config))
        return changes

    def _update_encode_table_button(self):
        button = getattr(self, "encode_table_button", None)
        if button is None:
            return
        button.setEnabled(self._connected_identity is not None
                          and self.encode_channel_combo.count() > 1
                          and self._netip_thread is None)

    def _open_encode_table(self):
        if not self._encode_configs:
            self._message("No encode settings fetched yet.")
            return
        dialog = EncodeTableDialog(self, self)
        dialog.exec()

    def _encode_resolution_changed(self, *_):
        if self._encode_mode != "nvr" or self._encode_current is None:
            return
        self._encode_store_current()
        self._refresh_encode_summary()

    def _refresh_encode_summary(self):
        grid = self.encode_summary_grid
        while grid.count():
            item = grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        if self._encode_mode != "nvr" or not self._encode_configs:
            self.encode_summary_group.setVisible(False)
            return
        for chn in range(len(self._encode_configs)):
            entry = self._encode_entry(chn)
            if isinstance(entry, dict):
                main = entry.get("MainFormat") if isinstance(
                    entry.get("MainFormat"), dict) else {}
                extra = entry.get("ExtraFormat") if isinstance(
                    entry.get("ExtraFormat"), dict) else {}
                main_video = main.get("Video") if isinstance(
                    main.get("Video"), dict) else {}
                extra_video = extra.get("Video") if isinstance(
                    extra.get("Video"), dict) else {}
                main_res = str(main_video.get("Resolution") or "—")
                sub_res = str(extra_video.get("Resolution") or "—")
            else:
                main_res = sub_res = "—"
            name = (self._encode_channel_names[chn]
                    if chn < len(self._encode_channel_names) else "")
            label = QLabel("CAM%02d  %s / %s" % (chn + 1, main_res, sub_res))
            label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse)
            details = "Channel %d" % (chn + 1)
            if name:
                details += ": %s" % name
            label.setToolTip("%s\nMain: %s\nSub: %s" % (
                details, main_res, sub_res))
            grid.addWidget(label, chn // 2, chn % 2)
        self.encode_summary_group.setVisible(True)

    def _encode_apply(self):
        self._encode_store_current()
        if self._encode_mode == "nvr":
            channels = []
            for chn, config in enumerate(self._encode_configs):
                if isinstance(config, list) and config and isinstance(config[0], dict):
                    channels.append((chn, config))
            if not channels:
                self._message("No encode settings to apply.")
                return
            self._start_system_action(
                "apply",
                changes={"encode_channels": channels,
                         "encode_smart": self._encode_smart_changes()},
                label="Applying encode settings on")
        elif self._encode_mode == "av" and self._encode_av_enc is not None:
            self._start_system_action(
                "apply",
                changes={"av_encode": self._encode_av_enc,
                         "encode_smart": self._encode_smart_changes()},
                label="Applying encode settings on")
        else:
            self._message("No encode settings fetched yet.")

    def _camera_param(self, chn):
        if chn is not None and 0 <= chn < len(self._camera_configs):
            config = self._camera_configs[chn]
            if isinstance(config, dict) and "Ret" not in config:
                return config
        return None

    def _camera_ex_param(self, chn):
        if chn is not None and 0 <= chn < len(self._camera_ex_configs):
            config = self._camera_ex_configs[chn]
            if isinstance(config, dict) and "Ret" not in config:
                return config
        return None

    def _white_light_param(self, chn):
        if chn is not None and 0 <= chn < len(self._white_light_configs):
            config = self._white_light_configs[chn]
            if isinstance(config, dict) and "Ret" not in config:
                return config
        return None

    @staticmethod
    def _to_int_value(value):
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        try:
            return int(str(value), 0)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _field_read(param, field, paths):
        parent, key = paths.get(field, (None, field))
        if parent is not None:
            source = param.get(parent)
            if not isinstance(source, dict):
                return None
        else:
            source = param
        return source.get(key)

    @staticmethod
    def _field_write(param, field, value, paths):
        parent, key = paths.get(field, (None, field))
        if parent is not None:
            source = param.get(parent)
            if not isinstance(source, dict):
                source = {}
                param[parent] = source
        else:
            source = param
        if isinstance(source.get(key), str):
            try:
                value = "0x%08X" % (int(value) & 0xFFFFFFFF)
            except (TypeError, ValueError):
                pass
        source[key] = value

    def _load_field_widgets(self, widgets, param, paths):
        for key, widget in widgets.items():
            if param is None:
                widget.setEnabled(False)
                continue
            value = self._field_read(param, key, paths)
            if value is None:
                widget.setEnabled(False)
                continue
            if isinstance(widget, QComboBox):
                index = widget.findData(value)
                if index < 0:
                    raw = self._to_int_value(value)
                    if raw is not None:
                        index = widget.findData(raw)
                        if index < 0:
                            widget.addItem("0x%X" % raw, raw)
                            index = widget.count() - 1
                    else:
                        widget.addItem(str(value), value)
                        index = widget.count() - 1
                widget.setCurrentIndex(index)
            elif isinstance(widget, QCheckBox):
                raw = self._to_int_value(value)
                if raw is None:
                    widget.setEnabled(False)
                    continue
                widget.setChecked(bool(raw))
            else:
                raw = self._to_int_value(value)
                if raw is None:
                    widget.setEnabled(False)
                    continue
                widget.setValue(min(max(raw, widget.minimum()), widget.maximum()))
            widget.setEnabled(True)

    def _store_field_widgets(self, widgets, param, paths):
        if param is None:
            return
        for key, widget in widgets.items():
            if not widget.isEnabled():
                continue
            if isinstance(widget, QComboBox):
                value = widget.currentData()
                if value is None:
                    continue
            elif isinstance(widget, QCheckBox):
                value = 1 if widget.isChecked() else 0
            else:
                value = widget.value()
            self._field_write(param, key, value, paths)

    def _camera_load(self, chn):
        self._camera_current = chn
        self._load_field_widgets(
            self.camera_widgets, self._camera_param(chn), CAMERA_FIELD_PATHS)
        self._load_field_widgets(
            self.camera_ex_widgets, self._camera_ex_param(chn),
            CAMERA_EX_FIELD_PATHS)
        self._load_field_widgets(
            self.white_light_widgets, self._white_light_param(chn),
            WHITE_LIGHT_FIELD_PATHS)

    def _camera_channel_changed(self, *_):
        self._camera_store_current()
        self._camera_load(self.camera_channel_combo.currentData())

    def _camera_store_current(self):
        self._store_field_widgets(
            self.camera_widgets, self._camera_param(self._camera_current),
            CAMERA_FIELD_PATHS)
        self._store_field_widgets(
            self.camera_ex_widgets, self._camera_ex_param(self._camera_current),
            CAMERA_EX_FIELD_PATHS)
        self._store_field_widgets(
            self.white_light_widgets, self._white_light_param(self._camera_current),
            WHITE_LIGHT_FIELD_PATHS)

    def _fill_camera_tab(self, payload):
        configs = payload.get("camera_param")
        self._camera_configs = configs if isinstance(configs, list) else []
        if "camera_ex_param" in payload:
            ex_configs = payload.get("camera_ex_param")
            self._camera_ex_configs = (
                ex_configs if isinstance(ex_configs, list) else [])
        lights = payload.get("white_light")
        self._white_light_configs = lights if isinstance(lights, list) else []
        self._camera_indexed = self._encode_mode == "nvr"
        combo = self.camera_channel_combo
        combo.blockSignals(True)
        combo.clear()
        for chn in range(len(self._camera_configs)):
            combo.addItem("CAM%02d" % (chn + 1), chn)
        target = 0
        for chn, config in enumerate(self._camera_configs):
            if isinstance(config, dict) and "Ret" not in config:
                target = chn
                break
        combo.setCurrentIndex(target if self._camera_configs else -1)
        combo.blockSignals(False)
        self._camera_current = None
        self._camera_load(combo.currentData() if self._camera_configs else None)

    def _camera_apply(self):
        self._camera_store_current()
        channels = []
        for chn, config in enumerate(self._camera_configs):
            if isinstance(config, dict) and "Ret" not in config:
                channels.append((chn, config))
        ex_channels = []
        for chn, config in enumerate(self._camera_ex_configs):
            if isinstance(config, dict) and "Ret" not in config:
                ex_channels.append((chn, config))
        if not channels and not ex_channels:
            self._message("No camera settings to apply.")
            return
        changes = {}
        if channels:
            changes["camera_param"] = channels
        if ex_channels:
            changes["camera_ex_param"] = ex_channels
        white = []
        for chn, config in enumerate(self._white_light_configs):
            if isinstance(config, dict) and "Ret" not in config:
                if self._camera_indexed:
                    command = "Camera.WhiteLight.[%d]" % chn
                else:
                    command = "Camera.WhiteLight"
                white.append((command, config))
        if white:
            changes["white_light"] = white
        self._start_system_action(
            "apply", changes=changes, label="Applying camera settings on")

    @staticmethod
    def _format_space(value):
        try:
            kb = int(str(value), 0)
        except (TypeError, ValueError):
            return ""
        if kb <= 0:
            return "0"
        gb = kb / (1024.0 * 1024.0)
        if gb >= 1024:
            return "%.2f TB" % (gb / 1024.0)
        if gb >= 1:
            return "%.2f GB" % gb
        return "%.1f MB" % (kb / 1024.0)

    def _fill_storage_tab(self, payload):
        raw = payload.get("storage_info")
        if isinstance(raw, dict):
            disks = raw.get("StorageInfo") if isinstance(raw.get("StorageInfo"), list) else []
        elif isinstance(raw, list):
            disks = raw
        else:
            disks = []
        rows = []
        self._storage_parts = []
        for disk in disks:
            if not isinstance(disk, dict):
                continue
            try:
                serial = int(disk.get("PlysicalNo"))
            except (TypeError, ValueError):
                serial = 0
            physical = serial + 1
            try:
                part_number = int(disk.get("PartNumber"))
            except (TypeError, ValueError):
                part_number = 0
            parts = disk.get("Partition") if isinstance(disk.get("Partition"), list) else []
            if part_number == 255:
                rows.append(("%d-1" % physical, "Unformatted", "", "", "", "", ""))
                self._storage_parts.append((serial, 0))
                continue
            for index in range(max(0, part_number)):
                part = parts[index] if index < len(parts) else {}
                if not isinstance(part, dict):
                    part = {}
                rows.append((
                    "%d-%d" % (physical, index + 1),
                    STORAGE_DRIVE_TYPES.get(
                        part.get("DirverType"), str(part.get("DirverType") or "")),
                    "Normal" if part.get("Status") == 0 else "Error",
                    self._format_space(part.get("TotalSpace")),
                    self._format_space(part.get("RemainSpace")),
                    str(part.get("NewStartTime") or ""),
                    str(part.get("NewEndTime") or "")))
                self._storage_parts.append((serial, index))
        table = self.storage_table
        table.setRowCount(len(rows))
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                table.setItem(row, column, QTableWidgetItem(value))
        table.resizeColumnsToContents()
        date_width = max(
            table.columnWidth(STORAGE_COLUMNS.index("Start")),
            table.columnWidth(STORAGE_COLUMNS.index("End")),
            table.fontMetrics().horizontalAdvance("0000-00-00 00:00:00") + 12)
        table.setColumnWidth(STORAGE_COLUMNS.index("Start"), date_width)
        table.setColumnWidth(STORAGE_COLUMNS.index("End"), date_width)
        header_height = table.horizontalHeader().height()
        row_height = table.verticalHeader().defaultSectionSize()
        table.setMaximumHeight(
            header_height + row_height * max(8, len(rows)) + table.frameWidth() * 2 + 2)
        if rows:
            table.selectRow(0)

    def _storage_selected_part(self):
        rows = self.storage_table.selectionModel().selectedRows()
        if not rows:
            self._message("Select a disk first.")
            return None
        row = rows[0].row()
        if 0 <= row < len(self._storage_parts):
            return self._storage_parts[row]
        return None

    def _storage_action(self, action, extra=None, confirm=None, label=""):
        part = self._storage_selected_part()
        if part is None:
            return
        serial, part_no = part
        if confirm:
            answer = QMessageBox.warning(
                self, "Storage",
                "%s %d-%d?" % (confirm, serial + 1, part_no + 1),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return
        payload = {"Action": action, "SerialNo": serial, "PartNo": part_no}
        if extra:
            payload.update(extra)
        self._start_system_action(
            "storage_action", changes={"payload": payload},
            label=label or (action + " on"),
            on_applied=self._on_storage_applied)

    def _storage_set_type(self, set_type):
        self._storage_action(
            "SetType", {"Type": set_type},
            label="Setting %s on" % set_type)

    def _storage_refresh(self):
        self._start_system_action(
            "storage_info", label="Reading storage info on",
            on_fetched=self._on_storage_fetched)

    def _on_storage_fetched(self, payload):
        self._fill_storage_tab(payload)

    def _on_storage_applied(self, results):
        info = results.pop("storage_info", None)
        if info is not None:
            self._fill_storage_tab({"storage_info": info})
        reply = results.get("OPStorageManager")
        ret = reply.get("Ret") if isinstance(reply, dict) else None
        text = RESULT_CODES.get(ret)
        if ret == 100:
            self._message("Storage: OK")
        elif ret == 603:
            self._message("Storage: Ret=603 (%s)" % (text or "reboot required"))
        else:
            self._message("Storage: Ret=%s%s" % (ret, " (%s)" % text if text else ""))

    @staticmethod
    def _select_combo_value(combo, value):
        if value is None:
            return
        index = combo.findData(value)
        if index < 0:
            index = combo.findData(str(value))
        if index >= 0:
            combo.setCurrentIndex(index)

    def _load_uart_entry(self, entry, protocol_combo, baud_combo, data_combo,
                         stop_combo, parity_combo):
        widgets = (protocol_combo, baud_combo, data_combo, stop_combo, parity_combo)
        if not isinstance(entry, dict):
            for widget in widgets:
                widget.setEnabled(False)
            return
        protocol = str(entry.get("ProtocolName") or "")
        if protocol and protocol_combo.findText(protocol) < 0:
            protocol_combo.addItem(protocol, protocol)
        protocol_combo.setCurrentText(protocol)
        attribute = entry.get("Attribute") if isinstance(entry.get("Attribute"), list) else []
        values = [attribute[index] if index < len(attribute) else None for index in range(4)]
        self._select_combo_value(baud_combo, values[0])
        self._select_combo_value(parity_combo, str(values[1] or "None"))
        self._select_combo_value(data_combo, values[2])
        self._select_combo_value(stop_combo, values[3])
        for widget in widgets:
            widget.setEnabled(True)

    def _store_uart_entry(self, entry, protocol_combo, baud_combo, data_combo,
                          stop_combo, parity_combo):
        if not isinstance(entry, dict):
            return
        entry["ProtocolName"] = protocol_combo.currentData() or protocol_combo.currentText()
        attribute = entry.get("Attribute") if isinstance(entry.get("Attribute"), list) else []
        while len(attribute) < 4:
            attribute.append(0)
        try:
            attribute[0] = int(baud_combo.currentData())
        except (TypeError, ValueError):
            attribute[0] = 9600
        attribute[1] = parity_combo.currentData() or "None"
        try:
            attribute[2] = int(data_combo.currentData())
        except (TypeError, ValueError):
            attribute[2] = 8
        try:
            attribute[3] = int(stop_combo.currentData())
        except (TypeError, ValueError):
            attribute[3] = 1
        entry["Attribute"] = attribute

    def _ptz_param(self, chn):
        if chn is not None and 0 <= chn < len(self._uart_ptz or []):
            entry = self._uart_ptz[chn]
            if isinstance(entry, dict):
                return entry
        return None

    def _ptz_load(self, chn):
        self._ptz_current = chn
        entry = self._ptz_param(chn)
        self._load_uart_entry(
            entry, self.ptz_protocol_combo, self.ptz_baud_combo,
            self.ptz_databits_combo, self.ptz_stopbits_combo, self.ptz_parity_combo)
        enabled = entry is not None
        if enabled:
            try:
                address = int(entry.get("DeviceNo") or 0)
            except (TypeError, ValueError):
                address = 0
            self.ptz_address_spin.setValue(address if 0 <= address <= 255 else 0)
        self.ptz_address_spin.setEnabled(enabled)

    def _ptz_channel_changed(self, *_):
        self._ptz_store_current()
        self._ptz_load(self.ptz_channel_combo.currentData())

    def _ptz_store_current(self):
        entry = self._ptz_param(self._ptz_current)
        if entry is None:
            return
        self._store_uart_entry(
            entry, self.ptz_protocol_combo, self.ptz_baud_combo,
            self.ptz_databits_combo, self.ptz_stopbits_combo, self.ptz_parity_combo)
        entry["DeviceNo"] = int(self.ptz_address_spin.value())

    def _fill_serial_ptz_tab(self, payload):
        comm = payload.get("uart_comm")
        self._uart_comm = comm if isinstance(comm, list) and comm else None
        ptz = payload.get("uart_ptz")
        self._uart_ptz = ptz if isinstance(ptz, list) and ptz else None
        rs485 = payload.get("uart_rs485")
        self._uart_rs485 = rs485 if isinstance(rs485, list) and rs485 else None
        for combo, key in ((self.rs232_function_combo, "com_protocol"),
                           (self.ptz_protocol_combo, "ptz_protocol"),
                           (self.rs485_protocol_combo, "uart_protocol")):
            names = payload.get(key)
            if isinstance(names, list) and names:
                combo.clear()
                for name in names:
                    combo.addItem(str(name), str(name))
        comm_entry = self._uart_comm[0] if self._uart_comm else None
        self._load_uart_entry(
            comm_entry, self.rs232_function_combo, self.rs232_baud_combo,
            self.rs232_databits_combo, self.rs232_stopbits_combo, self.rs232_parity_combo)
        combo = self.ptz_channel_combo
        combo.blockSignals(True)
        combo.clear()
        for chn in range(len(self._uart_ptz or [])):
            combo.addItem("CAM%02d" % (chn + 1), chn)
        combo.setCurrentIndex(0 if self._uart_ptz else -1)
        combo.blockSignals(False)
        self._ptz_current = None
        self._ptz_load(0 if self._uart_ptz else None)
        rs485_entry = self._uart_rs485[0] if self._uart_rs485 else None
        self._load_uart_entry(
            rs485_entry, self.rs485_protocol_combo, self.rs485_baud_combo,
            self.rs485_databits_combo, self.rs485_stopbits_combo, self.rs485_parity_combo)
        if rs485_entry is not None:
            try:
                address = int(rs485_entry.get("DeviceNo") or 0)
            except (TypeError, ValueError):
                address = 0
            self.rs485_address_spin.setValue(address if 0 <= address <= 255 else 0)
        self.rs485_address_spin.setEnabled(rs485_entry is not None)

    def _serial_ptz_apply(self):
        self._ptz_store_current()
        changes = {}
        if self._uart_comm:
            self._store_uart_entry(
                self._uart_comm[0], self.rs232_function_combo, self.rs232_baud_combo,
                self.rs232_databits_combo, self.rs232_stopbits_combo,
                self.rs232_parity_combo)
            changes["uart_comm"] = self._uart_comm
        if self._uart_ptz:
            changes["uart_ptz"] = self._uart_ptz
        if self._uart_rs485:
            self._store_uart_entry(
                self._uart_rs485[0], self.rs485_protocol_combo, self.rs485_baud_combo,
                self.rs485_databits_combo, self.rs485_stopbits_combo,
                self.rs485_parity_combo)
            self._uart_rs485[0]["DeviceNo"] = int(self.rs485_address_spin.value())
            changes["uart_rs485"] = self._uart_rs485
        if not changes:
            self._message("No serial/PTZ settings to apply.")
            return
        self._start_system_action(
            "apply", changes=changes, label="Applying serial/PTZ settings on")

    def _fill_users_tab(self, payload):
        users_reply = payload.get("users") if isinstance(payload.get("users"), dict) else {}
        self._users = users_reply.get("Users") if isinstance(
            users_reply.get("Users"), list) else []
        groups_reply = payload.get("groups") if isinstance(payload.get("groups"), dict) else {}
        self._groups = groups_reply.get("Groups") if isinstance(
            groups_reply.get("Groups"), list) else []
        authorities_reply = payload.get("authority_list") if isinstance(
            payload.get("authority_list"), dict) else {}
        authorities = authorities_reply.get("AuthorityList")
        if isinstance(authorities, list) and authorities:
            self._authorities = authorities
        table = self.users_table
        table.setRowCount(len(self._users))
        for row, user in enumerate(self._users):
            if not isinstance(user, dict):
                user = {}
            values = (str(row + 1), str(user.get("Name") or ""),
                      str(user.get("Group") or ""))
            for column, value in enumerate(values):
                table.setItem(row, column, QTableWidgetItem(value))
        table.resizeColumnsToContents()
        if self._users:
            table.selectRow(0)
        groups = self.groups_table
        groups.setRowCount(len(self._groups))
        for row, group in enumerate(self._groups):
            if not isinstance(group, dict):
                group = {}
            values = (str(row + 1), str(group.get("Name") or ""))
            for column, value in enumerate(values):
                groups.setItem(row, column, QTableWidgetItem(value))
        groups.resizeColumnsToContents()
        if self._groups:
            groups.selectRow(0)

    def _selected_user(self):
        rows = self.users_table.selectionModel().selectedRows()
        if not rows:
            self._message("Select a user first.")
            return None
        row = rows[0].row()
        if 0 <= row < len(self._users):
            user = self._users[row]
            if isinstance(user, dict):
                return user
        return None

    def _selected_group(self):
        rows = self.groups_table.selectionModel().selectedRows()
        if not rows:
            self._message("Select a group first.")
            return None
        row = rows[0].row()
        if 0 <= row < len(self._groups):
            group = self._groups[row]
            if isinstance(group, dict):
                return group
        return None

    def _group_authorities(self, name):
        for group in self._groups:
            if isinstance(group, dict) and str(group.get("Name")) == name:
                authorities = group.get("AuthorityList")
                if isinstance(authorities, list):
                    return authorities
        return []

    def _user_add(self):
        if not self._groups:
            self._message("No groups available.")
            return
        dialog = UserDialog(self, self._groups, self._authorities)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        if not values["name"]:
            self._message("User name is required.")
            return
        if values["password"] != values["confirm"]:
            self._message("Passwords do not match.")
            return
        self._start_system_action(
            "user_add", changes={"values": values},
            label="Adding user on", on_applied=self._on_users_applied)

    def _user_modify(self):
        user = self._selected_user()
        if user is None:
            return
        dialog = UserDialog(self, self._groups, self._authorities, user=user)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        if not values["name"]:
            self._message("User name is required.")
            return
        self._start_system_action(
            "user_modify",
            changes={"values": values, "user": dict(user),
                     "original": str(user.get("Name") or "")},
            label="Modifying user on", on_applied=self._on_users_applied)

    def _user_delete(self):
        user = self._selected_user()
        if user is None:
            return
        if user.get("Reserved") or str(user.get("Name")) == "admin":
            self._message("This user cannot be deleted.")
            return
        answer = QMessageBox.warning(
            self, "Users", "Delete user %s?" % user.get("Name"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._start_system_action(
            "user_delete", changes={"values": {"name": str(user.get("Name") or "")}},
            label="Deleting user on", on_applied=self._on_users_applied)

    def _user_password(self):
        user = self._selected_user()
        if user is None:
            return
        name = str(user.get("Name") or "")
        dialog = PasswordDialog(name, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        old_password, new_password = dialog.values()
        if not new_password:
            self._message("New password is empty.")
            return
        self._start_system_action(
            "user_password",
            changes={"values": {"name": name, "old": old_password, "new": new_password}},
            label="Changing password on", on_applied=self._on_users_applied)

    def _group_add(self):
        dialog = GroupDialog(self, self._authorities)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        if not values["name"]:
            self._message("Group name is required.")
            return
        self._start_system_action(
            "group_add", changes={"values": values},
            label="Adding group on", on_applied=self._on_users_applied)

    def _group_modify(self):
        group = self._selected_group()
        if group is None:
            return
        dialog = GroupDialog(self, self._authorities, group=group)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        if not values["name"]:
            self._message("Group name is required.")
            return
        self._start_system_action(
            "group_modify",
            changes={"values": values, "original": str(group.get("Name") or "")},
            label="Modifying group on", on_applied=self._on_users_applied)

    def _group_delete(self):
        group = self._selected_group()
        if group is None:
            return
        name = str(group.get("Name") or "")
        if name in ("admin", "user"):
            self._message("This group cannot be deleted.")
            return
        if any(isinstance(user, dict) and str(user.get("Group")) == name
               for user in self._users):
            self._message("Group is in use.")
            return
        answer = QMessageBox.warning(
            self, "Users", "Delete group %s?" % name,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._start_system_action(
            "group_delete", changes={"values": {"name": name}},
            label="Deleting group on", on_applied=self._on_users_applied)

    def _users_refresh(self):
        self._start_system_action(
            "users_info", label="Reading users on",
            on_fetched=self._on_users_fetched)

    def _on_users_fetched(self, payload):
        self._fill_users_tab(payload)

    def _on_users_applied(self, results):
        if "users" in results or "groups" in results:
            self._fill_users_tab({
                "users": results.get("users"), "groups": results.get("groups")})
        for key in ("user_add", "user_modify", "user_delete", "user_password",
                    "group_add", "group_modify", "group_delete"):
            reply = results.get(key)
            if not isinstance(reply, dict):
                continue
            ret = reply.get("Ret")
            text = RESULT_CODES.get(ret)
            if ret == 100:
                self._message("Users: OK")
            else:
                self._message("Users: Ret=%s%s" % (ret, " (%s)" % text if text else ""))
            return

    def _system_sync_time(self):
        self._start_system_action("sync_time", label="Syncing time on")

    @staticmethod
    def _app_dir():
        """Folder the app runs from (the PyInstaller onedir folder when frozen)."""
        if getattr(sys, "frozen", False):
            return os.path.dirname(os.path.abspath(sys.executable))
        return HERE

    def add_system_button(self, text, callback, tooltip=""):
        """Append a local/private action below the System tab buttons."""
        grid = getattr(self, "system_buttons_grid", None)
        if grid is None:
            return None
        button = QPushButton(text)
        if tooltip:
            button.setToolTip(tooltip)
        button.setMaximumWidth(84)
        button.clicked.connect(callback)
        grid.addWidget(button, grid.rowCount(), 0)
        button.setEnabled(
            getattr(self, "_connected_identity", None) is not None)
        return button

    def _open_app_dir(self):
        path = self._app_dir()
        if not os.path.isdir(path):
            path = os.path.expanduser("~")
        try:
            if sys.platform.startswith("win") and hasattr(os, "startfile"):
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(
                    ["open", path], stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(
                    ["xdg-open", path], stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
        except OSError as error:
            self._message("Cannot open %s: %s" % (path, error))

    def _config_dir(self):
        if getattr(sys, "frozen", False):
            base = os.path.dirname(os.path.abspath(sys.executable))
            path = os.path.join(base, "cfgs")
            try:
                os.makedirs(path, exist_ok=True)
                probe = os.path.join(path, ".writable")
                with open(probe, "w"):
                    pass
                os.remove(probe)
                return path
            except OSError:
                pass
            base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
            path = os.path.join(base, "xmdm3", "cfgs")
        else:
            path = os.path.join(HERE, "cfgs")
        try:
            os.makedirs(path, exist_ok=True)
        except OSError:
            pass
        return path

    def _export_config(self):
        device = self._system_target()
        if not isinstance(device, dict):
            self._message("No device selected — pick a table row first.")
            return
        self._start_system_action(
            "config_export", device=device, label="Exporting config from",
            on_applied=self._on_config_exported)

    def _on_config_exported(self, results):
        data = results.get("config_export")
        if not isinstance(data, (bytes, bytearray)):
            self._message("Config export failed: %s" % (results,))
            return
        info = {}
        if isinstance(self._fetched_payload, dict):
            info = self._fetched_payload.get("system") or {}

        def clean(value, fallback):
            value = "".join(ch for ch in str(value)
                            if ch.isalnum() or ch in "._-")
            return value or fallback

        hardware = clean(info.get("HardWare") or self.system_hardware_edit.text(),
                         "device")
        software = str(info.get("SoftWareVersion")
                       or self.system_software_edit.text()).strip()
        parts = software.split(".", 3)
        build = clean(parts[3][:8] if len(parts) > 3 else software[:8], "build")
        device = self._system_target() or {}
        serial = clean(info.get("SerialNo") or device.get("sn")
                       or device.get("cloud_id"), "nosn")
        filename = "%s-%s-%s-%s.cfg" % (
            hardware, build, serial, time.strftime("%Y%m%d%H%M%S"))
        path = os.path.join(self._config_dir(), filename)
        try:
            with open(path, "wb") as handle:
                handle.write(bytes(data))
        except OSError as error:
            self._message("Config export failed: %s" % error)
            return
        self._message("Config exported to %s" % path)

    def _import_config(self):
        device = self._system_target()
        if not isinstance(device, dict):
            self._message("No device selected — pick a table row first.")
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Import config", self._config_dir(), "Config files (*.cfg)")
        if not path:
            return
        try:
            with open(path, "rb") as handle:
                data = handle.read()
        except OSError as error:
            self._message("Config import failed: %s" % error)
            return
        self._start_system_action(
            "config_import", device=device,
            changes={"data": data},
            label="Importing config to",
            on_applied=self._on_config_imported)

    def _on_config_imported(self, results):
        reply = results.get("config_import")
        ret = reply.get("Ret") if isinstance(reply, dict) else None
        text = RESULT_CODES.get(ret)
        if reply is None:
            self._message("Config imported — device is restarting.")
        elif ret in (100, 603):
            self._message("Config imported — device needs a restart.")
        else:
            self._message("Config import: Ret=%s%s" % (
                ret, " (%s)" % text if text else ""))

    def _reset_config(self):
        device = self._system_target()
        if not isinstance(device, dict):
            self._message("No device selected — pick a table row first.")
            return
        dialog = ResetConfigDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        if dialog.full_reset:
            warning = ("Full reset to factory defaults on %s?\n\n"
                       "Accounts and network settings are kept; the device will "
                       "need a restart." % (device.get("ip") or ""))
        else:
            warning = "Reset the selected config sections on %s?" % (
                device.get("ip") or "")
        answer = QMessageBox.warning(
            self, "Reset config", warning,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._start_system_action(
            "reset_config", changes={"config": dialog.payload()},
            label="Resetting config on", on_applied=self._on_reset_applied)

    def _on_reset_applied(self, results):
        reply = results.get("OPDefaultConfig")
        ret = reply.get("Ret") if isinstance(reply, dict) else None
        if ret == 100:
            self._message("Config reset done.")
        elif ret == 603:
            self._message("Config reset — device needs a restart.")
        else:
            text = RESULT_CODES.get(ret)
            self._message("Config reset: Ret=%s%s" % (
                ret, " (%s)" % text if text else ""))

    def _recovery_image(self):
        dialog = RecoveryDialog(self)
        dialog.exec()

    def _dump_image(self):
        dialog = DumpDialog(self)
        dialog.exec()

    def _view_logs(self):
        self._start_system_action("logs", label="Reading logs from",
                                  on_fetched=self._on_logs_fetched)

    def _on_logs_fetched(self, payload):
        reply = payload.get("logs")
        logs = reply.get("OPLogQuery") if isinstance(reply, dict) else None
        if not isinstance(logs, list):
            self._message("No logs returned.")
            return
        lines = []
        for log in logs:
            if not isinstance(log, dict):
                continue
            lines.append("%s %10s %-12s %s" % (
                log.get("Time", ""), log.get("User", ""),
                log.get("Type", ""), log.get("Data", "")))
        device = self._system_target()
        name = device.get("ip") if isinstance(device, dict) else ""
        dialog = QDialog(self)
        dialog.setWindowTitle("Device logs — %s" % name)
        dialog.resize(900, 600)
        view = QPlainTextEdit("\n".join(lines))
        view.setReadOnly(True)
        layout = QVBoxLayout(dialog)
        layout.addWidget(view)
        dialog.show()

    def _erase_logs(self):
        device = self._system_target()
        if not isinstance(device, dict):
            self._message("No device selected — pick a table row first.")
            return
        answer = QMessageBox.question(
            self, "Erase logs",
            "Erase all logs on %s?" % (device.get("ip") or ""))
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._start_system_action("erase_logs", label="Erasing logs on")

    def _browse_firmware(self):
        settings = QSettings("xmdm3", "xmdms")
        current = self.network_upgrade_file_edit.text().strip()
        start_dir = os.path.dirname(current) or settings.value(
            "firmware_dir", "", type=str)
        path, _ = QFileDialog.getOpenFileName(
            self, "Select firmware file", start_dir, "Firmware files (*.bin)")
        if path:
            self.network_upgrade_file_edit.setText(path)
            settings.setValue("firmware_dir", os.path.dirname(path))

    def _upgrade_firmware(self):
        device = self._system_target()
        if not isinstance(device, dict):
            self._message("No device selected — pick a table row first.")
            return
        path = self.network_upgrade_file_edit.text().strip()
        if not path:
            self._browse_firmware()
            path = self.network_upgrade_file_edit.text().strip()
        if not path:
            return
        answer = QMessageBox.question(
            self, "Upgrade firmware",
            "Upload %s to %s?\n\nThe device will upgrade and may reboot." % (
                os.path.basename(path), device.get("ip") or ""))
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._start_system_action(
            "upgrade", changes={"filename": path},
            label="Uploading firmware to", device=device)

    def _cloud_upgrade(self):
        device = self._system_target()
        if not isinstance(device, dict):
            self._message("No device selected — pick a table row first.")
            return
        self._start_system_action(
            "cloud_upgrade_list", label="Checking cloud upgrade for",
            device=device, on_fetched=self._on_cloud_versions)

    def _on_cloud_versions(self, payload):
        reply = payload.get("version_list")
        version = reply.get("OPVersionList") if isinstance(reply, dict) else None
        if not version:
            self._message("No cloud upgrade info (device may not support it).")
            return
        text = json.dumps(version, indent=2, ensure_ascii=False)
        if len(text) > 1200:
            text = text[:1200] + " ..."
        answer = QMessageBox.question(
            self, "Cloud upgrade", "Start cloud upgrade?\n\n%s" % text)
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._start_system_action(
            "cloud_upgrade_apply", changes={"version": version},
            label="Starting cloud upgrade on",
            on_applied=self._on_cloud_upgrade_started)

    def _on_cloud_upgrade_started(self, results):
        reply = results.get("OPReqVersion")
        ret = reply.get("Ret") if isinstance(reply, dict) else None
        self._message("Cloud upgrade: Ret=%s (%s)" % (
            ret, RESULT_CODES.get(ret, "unknown")))

    def _open_channels(self):
        device = self._system_target()
        if not isinstance(device, dict):
            self._message("No device selected — pick a table row first.")
            return
        if self._channels_dialog is not None:
            self._channels_dialog.close()
            self._channels_dialog.deleteLater()
            self._channels_dialog = None
        username, password = self._device_credentials(device)
        dialog = DigitalChannelsDialog(
            device, username, password, parent=self)
        self._channels_dialog = dialog
        dialog.show()
        self._message("Digital channels: %s" % (device.get("ip") or ""))

    def _system_reboot(self):
        device = self._system_target()
        if not isinstance(device, dict):
            self._message("No device selected — pick a table row first.")
            return
        answer = QMessageBox.question(
            self, "Reboot device", "Reboot %s?" % (device.get("ip") or ""))
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._start_system_action("reboot", label="Rebooting")

    def _on_system_fetched(self, payload, quiet=False):
        sender = self.sender()
        if isinstance(sender, NetipThread) and sender is not self._netip_thread:
            return
        merged = dict(self._fetched_payload or {})
        merged.update(payload)
        payload = merged
        self._system_payload = merged
        self._fetched_payload = merged
        self._fetched_keys.update(payload.keys())
        info = payload.get("system") if isinstance(payload.get("system"), dict) else {}
        common = payload.get("common") if isinstance(payload.get("common"), dict) else {}
        general = payload.get("general") if isinstance(payload.get("general"), dict) else {}
        device_desc = payload.get("device_desc") if isinstance(
            payload.get("device_desc"), dict) else {}
        target = self._system_target()
        self._fetched_identity = (
            DeviceTableModel.identity(target) if isinstance(target, dict) else None)
        if isinstance(target, dict) and common:
            raw = target.get("raw") or {}
            raw.update(common)
            for key in ("SoftWareVersion", "BuildTime", "DeviceType", "SerialNo"):
                if info.get(key) is not None:
                    raw[key] = info.get(key)
            target["raw"] = raw
            target["mac"] = common.get("MAC") or target.get("mac") or ""
            target["host_name"] = (common.get("HostName") or info.get("HardWare")
                                   or target.get("host_name") or "")
            target["version"] = str(info.get("SoftWareVersion")
                                    or target.get("version") or "")
            target["build_date"] = normalize_build_time(
                info.get("BuildTime") or target.get("build_date"))
            if target.get("device_type") is None:
                target["device_type"] = (info.get("DeviceType")
                                         if info.get("DeviceType") is not None
                                         else common.get("DeviceType"))
            target["http_port"] = common.get("HttpPort") or target.get("http_port")
            target["tcp_port"] = common.get("TCPPort") or target.get("tcp_port")
            self.model.upsert(target)
        network_keys = ("common", "dhcp", "adaptive", "dns", "smartnet", "wifi",
                        "rtsp", "online_upgrade", "upnp", "onvif_pwd", "pms", "ntp",
                        "pubcfg", "caps", "force_dhcp", "disable_xm_server", "nat",
                        "ability", "oemcfg")
        if any(key in payload for key in network_keys):
            self._fill_network_from_fetch(
                common, payload.get("dhcp"), payload.get("adaptive"),
                payload.get("dns"), payload.get("smartnet"), general,
                payload.get("wifi"), payload.get("rtsp"),
                payload.get("online_upgrade"), payload.get("upnp"),
                payload.get("onvif_pwd"), payload.get("pms"), payload.get("ntp"),
                payload.get("pubcfg"), payload.get("caps"),
                payload.get("force_dhcp"), payload.get("disable_xm_server"),
                payload.get("nat"), payload.get("ability"), payload.get("oemcfg"))

        languages = payload.get("languages")
        if isinstance(languages, list) and languages:
            self.system_language_combo.blockSignals(True)
            self.system_language_combo.clear()
            self.system_language_combo.addItems([str(item) for item in languages])
            self.system_language_combo.blockSignals(False)
        if any(key in payload for key in ("system", "common", "chn_status")):
            self.system_hardware_edit.setText(str(info.get("HardWare") or ""))
            self.system_software_edit.setText(str(info.get("SoftWareVersion") or ""))
            cloud = ""
            if isinstance(target, dict):
                cloud = str(target.get("cloud_id") or "")
            if not cloud:
                for key in ("CloudID", "CloudId", "P2PID", "P2PId", "UUID",
                            "CloudCode", "SerialNo", "SerialNumber", "SN"):
                    value = info.get(key) or common.get(key)
                    if value:
                        cloud = str(value)
                        break
            self.system_cloud_edit.setText(cloud)
            self.system_build_edit.setText(
                normalize_build_time(info.get("BuildTime")))
            device_type = info.get("DeviceType")
            if device_type is None:
                device_type = common.get("DeviceType")
            self.system_type_edit.setText(
                "" if device_type is None else self._device_type_name(device_type))
            age_source = info.get("BuildTime") or (
                target.get("build_date") if isinstance(target, dict) else "")
            self._age_build_time = age_source
            runtime = info.get("DeviceRunTime")
            runtime_text = format_device_runtime(runtime)
            if runtime_text:
                try:
                    minutes = (int(runtime, 16) if isinstance(runtime, str)
                               and runtime.strip().lower().startswith("0x")
                               else int(runtime))
                except (TypeError, ValueError):
                    minutes = None
                self._age_runtime = (minutes, time.time()) if minutes is not None else None
            else:
                self._age_runtime = None
            self.system_age_edit.setText(
                runtime_text or format_device_age(age_source))
            channels = (common.get("ChannelNum") or info.get("VideoInChannel")
                        or info.get("ChannelNum"))
            if not channels:
                status = payload.get("chn_status")
                if isinstance(status, list):
                    channels = sum(
                        1 for entry in status
                        if isinstance(entry, dict)
                        and (entry.get("ChnName") or entry.get("Status")))
            self.system_channels_edit.setText(
                "" if channels is None else str(channels))
            self._set_channel_count(channels)
        if "general" in payload:
            self._system_general_keys = {}
            location = general.get("Location") if isinstance(
                general.get("Location"), dict) else {}
            for field, candidates in SYSTEM_GENERAL_KEYS.items():
                for key in candidates:
                    if key in location:
                        self._system_general_keys[field] = key
                        break
                else:
                    for key in candidates:
                        if key in general:
                            self._system_general_keys[field] = key
                            break

            def general_value(field):
                key = self._system_general_keys.get(field)
                if not key:
                    return ""
                if key in location:
                    return location.get(key)
                return general.get(key)

            self.system_tv_combo.setCurrentText(str(general_value("tv_standard") or ""))
            self.system_language_combo.setCurrentText(
                str(general_value("language") or ""))
            self.system_date_combo.setCurrentText(
                str(general_value("date_format") or ""))
            self.system_separator_combo.setCurrentText(
                str(general_value("separator") or ""))
            hour = str(general_value("time_format") or "24")
            self.system_hour_combo.setCurrentIndex(
                1 if hour.strip() in ("12", "12H", "12h") else 0)
            maintain = general.get("AutoMaintain") if isinstance(
                general.get("AutoMaintain"), dict) else {}
            self.system_restart_day_combo.setCurrentIndex(
                self.system_restart_day_combo.findText(
                    str(maintain.get("AutoRebootDay") or "")))
            try:
                hour = int(maintain.get("AutoRebootHour"))
            except (TypeError, ValueError):
                hour = 0
            self.system_restart_hour_combo.setCurrentIndex(
                hour if 0 <= hour <= 23 else 0)
        if "max_preview" in payload:
            preview = payload.get("max_preview") if isinstance(
                payload.get("max_preview"), dict) else {}
            preview_num = preview.get("PreviewNum")
            support = preview.get("SupportChannel")
            values = []
            if isinstance(support, list):
                for value in support:
                    if value not in values:
                        values.append(value)
            if preview_num is not None and preview_num not in values:
                values.append(preview_num)
            if values:
                try:
                    values.sort()
                except TypeError:
                    pass
                self.system_maxchannels_combo.blockSignals(True)
                self.system_maxchannels_combo.clear()
                for value in values:
                    self.system_maxchannels_combo.addItem(str(value), value)
                self.system_maxchannels_combo.blockSignals(False)
            index = self.system_maxchannels_combo.findData(preview_num)
            if index >= 0:
                self.system_maxchannels_combo.setCurrentIndex(index)
        if "nat_info" in payload:
            nat_info = payload.get("nat_info") if isinstance(
                payload.get("nat_info"), dict) else {}
            self.system_nat_status_edit.setText(str(nat_info.get("NatStatus") or ""))
            self.system_nat_info_edit.setText(str(nat_info.get("NaInfoCode") or ""))
        if "system_timezone" in payload:
            timezone_config = payload.get("system_timezone") if isinstance(
                payload.get("system_timezone"), dict) else {}
            self._system_timezone_config = timezone_config
            try:
                time_min = int(timezone_config.get("timeMin"))
            except (TypeError, ValueError):
                time_min = None
            if time_min is not None:
                offset = -time_min
                index = self.system_timezone_combo.findData(offset)
                if index < 0:
                    label = "UTC%s%02d:%02d" % ("+" if offset >= 0 else "-",
                                                abs(offset) // 60, abs(offset) % 60)
                    self.system_timezone_combo.addItem(label, offset)
                    index = self.system_timezone_combo.count() - 1
                self.system_timezone_combo.setCurrentIndex(index)
        if "device_desc" in payload:
            self._system_device_desc_config = device_desc
            beep = device_desc.get("EnableBeep")
            try:
                beep_enabled = bool(int(str(beep), 0) & 1)
            except (TypeError, ValueError):
                beep_enabled = bool(beep)
            self.system_beeper_check.setChecked(beep_enabled)
        display_keys = ("video_out", "gui_set", "vga_resolution", "ability",
                        "device_desc")
        if any(key in payload for key in display_keys):
            vga = payload.get("vga_resolution") if isinstance(
                payload.get("vga_resolution"), dict) else {}
            entries = [item.strip() for item in str(
                vga.get("Resolution") or "").split("|")]
            entries = [item for item in entries if item]
            if entries:
                self.display_resolution_combo.blockSignals(True)
                self.display_resolution_combo.clear()
                for entry in entries:
                    base = entry.split("(")[0].strip()
                    if "*" not in base:
                        continue
                    width_text, height_text = base.split("*", 1)
                    try:
                        value = (int(width_text.strip()), int(height_text.strip()))
                    except ValueError:
                        continue
                    self.display_resolution_combo.addItem(
                        entry, "%dx%d" % value)
                self.display_resolution_combo.blockSignals(False)
            video_out = payload.get("video_out") if isinstance(
                payload.get("video_out"), dict) else {}
            self._display_video_out_config = video_out
            mode = video_out.get("Mode") if isinstance(
                video_out.get("Mode"), dict) else {}
            try:
                resolution = (int(mode.get("Width")), int(mode.get("Height")))
            except (TypeError, ValueError):
                resolution = None
            if resolution:
                key = "%dx%d" % resolution
                index = self.display_resolution_combo.findData(key)
                if index < 0:
                    self.display_resolution_combo.addItem(key, key)
                    index = self.display_resolution_combo.count() - 1
                self.display_resolution_combo.setCurrentIndex(index)
            gui_set = payload.get("gui_set") if isinstance(
                payload.get("gui_set"), dict) else {}
            gui_available = bool(gui_set) and "Ret" not in gui_set
            self._display_gui_set_config = gui_set if gui_available else {}
            for key, check in self._display_gui_checks.items():
                check.setEnabled(gui_available)
                if gui_available and key in gui_set:
                    check.setChecked(bool(gui_set.get(key)))
            self.display_window_alpha_spin.setEnabled(gui_available)
            if gui_available:
                try:
                    self.display_window_alpha_spin.setValue(
                        int(gui_set.get("WindowAlpha")))
                except (TypeError, ValueError):
                    self.display_window_alpha_spin.setValue(0)
            ability = payload.get("ability") if isinstance(
                payload.get("ability"), dict) else {}
            self.display_face_check.setChecked(
                bool(ability.get("FaceFunctionEnable")))
            self.display_debug_check.setChecked(
                bool(device_desc.get("EnableDebugMode")))
            audio = device_desc.get("AudioInChannel")
            self.display_audio_edit.setText(
                "" if audio is None else str(audio))
        if any(key in payload for key in ("encode_channels", "encode_smart",
                                          "encode_ability", "av_encode")):
            self._fill_encode_tab(payload)
        if any(key in payload for key in (
                "camera_param", "camera_ex_param", "white_light")):
            self._fill_camera_tab(payload)
        if "storage_info" in payload:
            self._fill_storage_tab(payload)
        if any(key in payload for key in ("uart_comm", "uart_ptz", "uart_rs485",
                                          "com_protocol", "ptz_protocol",
                                          "uart_protocol")):
            self._fill_serial_ptz_tab(payload)
        if any(key in payload for key in ("users", "groups", "authority_list")):
            self._fill_users_tab(payload)
        self._sync_selection_state()

    def _on_system_applied(self, results):
        sender = self.sender()
        if isinstance(sender, NetipThread) and sender is not self._netip_thread:
            return
        summary = []
        for name, reply in results.items():
            ret = reply.get("Ret") if isinstance(reply, dict) else None
            text = RESULT_CODES.get(ret)
            if ret == 100 or not text:
                summary.append("%s Ret=%s" % (name, ret))
            else:
                summary.append("%s Ret=%s (%s)" % (name, ret, text))
        self._message("NetIP: " + (", ".join(summary) if summary else "done"))

    def _on_system_failed(self, text, thread=None):
        if thread is not None and thread is not self._netip_thread:
            return
        if self._connect_pending is not None:
            self.model.set_connected(self._connect_pending, False)
            if self._connected_identity == self._connect_pending:
                self._connected_identity = None
            self._connect_pending = None
            self._set_connection_text("Disconnected")
        self._fetch_in_progress = False
        self._system_error = True
        self._message("NetIP error: %s" % text)
        if self._connected_identity is not None and is_connection_error(text):
            self._drop_connection()
        else:
            self._sync_selection_state()

    def _on_system_finished(self, thread=None):
        if thread is None:
            thread = self._netip_thread
        if thread is not self._netip_thread:
            if thread is not None:
                if thread in self._stale_threads:
                    self._stale_threads.remove(thread)
                thread.deleteLater()
            return
        self._netip_thread = None
        if thread is not None:
            if (getattr(thread, "_action", "") == "fetch"
                    and not self._system_error):
                self.fetch_label.setText("")
            thread.deleteLater()
        self._system_error = False
        self._set_system_busy(False)
        self._update_encode_table_button()
        self._fetch_in_progress = False
        if self._pending_fetch_keys and self._connected_identity is not None:
            pending = set(self._pending_fetch_keys)
            self._pending_fetch_keys = set()
            self._request_fetch(pending)

    def _table_context_menu(self, point):
        menu = QMenu(self)
        index = self.table.indexAt(point)
        text = table_cell_text(self.table, index)
        copy_action = menu.addAction("Copy")
        copy_action.setEnabled(bool(text))
        copy_action.triggered.connect(
            lambda: QApplication.clipboard().setText(text))
        menu.addSeparator()
        menu.addAction("Select all", lambda: self.model.set_all_checked(True))
        menu.addAction("Deselect all", lambda: self.model.set_all_checked(False))
        menu.addSeparator()
        menu.addAction("Add", self._add_device)
        menu.addAction("Modify", self._modify_device)
        menu.addAction("Delete", self._delete_device)
        menu.addAction("Clear", self._clear_devices)
        menu.exec(self.table.viewport().mapToGlobal(point))

    def _modify_device(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            self._message("Select a device first.")
            return
        row = rows[0].row()
        device = self.model.device_at(row)
        if device is None:
            return
        dialog = AddDeviceDialog(self)
        dialog.setWindowTitle("Modify device")
        dialog.set_values(device)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        cloud_id = dialog.cloud_id()
        address = dialog.address() if not cloud_id else ""
        if not address and not cloud_id:
            self._message("Invalid IP address.")
            return
        identity = DeviceTableModel.identity(device)
        updated = manual_device(
            address, dialog.port(), dialog.username(), dialog.password(),
            cloud_id=cloud_id, rps=dialog.rps())
        updated["no_md5"] = dialog.no_md5()
        for key in ("sn", "mac", "raw", "http_port", "subnet", "gateway"):
            if device.get(key):
                updated[key] = device[key]
        self.model.remove_device(row)
        self.model.upsert(updated)
        if self._connected_identity == identity:
            self._connected_identity = DeviceTableModel.identity(updated)
        self._message("Updated %s:%d" % (
            updated.get("cloud_id") or updated.get("ip") or "",
            updated.get("tcp_port") or 34567))

    def _delete_device(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            self._message("Select a device first.")
            return
        row = rows[0].row()
        device = self.model.device_at(row)
        if device is None:
            return
        identity = DeviceTableModel.identity(device)
        self.model.remove_device(row)
        if self._connected_identity == identity:
            self._connected_identity = None
        self._message("Deleted %s" % (device.get("ip") or identity))

    def _clear_devices(self):
        if self.model.rowCount() == 0:
            return
        answer = QMessageBox.question(self, "Clear devices", "Remove all discovered devices?")
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.model.clear()
        self._connected_identity = None
        self._message("Cleared.")

    def _target_device(self):
        checked = self.model.checked_devices()
        if checked:
            return checked[0]
        rows = self.table.selectionModel().selectedRows()
        if rows:
            return self.model.device_at(rows[0].row())
        return None

    def _set_channel_count(self, count):
        try:
            count = int(count)
        except (TypeError, ValueError):
            return
        self._channel_count = count
        self._update_channels_button()
        if count < 1 or self.channel_combo.count() == count:
            return
        current = self.channel_combo.currentData()
        self.channel_combo.blockSignals(True)
        self.channel_combo.clear()
        for channel in range(1, count + 1):
            self.channel_combo.addItem("CAM%02d" % channel, channel)
        if current is not None:
            index = self.channel_combo.findData(current)
            if index >= 0:
                self.channel_combo.setCurrentIndex(index)
        self.channel_combo.blockSignals(False)

    def _channel(self):
        return int(self.channel_combo.currentData() or 1)

    def _stream(self):
        return 0 if self.stream_main_radio.isChecked() else 1

    def _stream_radio_changed(self, checked):
        if checked:
            self._video_source_changed()

    def _add_device(self):
        dialog = AddDeviceDialog(self)
        dialog.set_user(self.user_edit.text().strip() or "admin")
        dialog.set_password(self.password_edit.text())
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        cloud_id = dialog.cloud_id()
        address = dialog.address() if not cloud_id else ""
        if not address and not cloud_id:
            self._message("Invalid IP address.")
            return
        device = manual_device(
            address, dialog.port(), dialog.username(), dialog.password(),
            cloud_id=cloud_id, rps=dialog.rps())
        device["no_md5"] = dialog.no_md5()
        self.model.upsert(device)
        if cloud_id:
            self._message("Added cloud device %s:%d" % (cloud_id, device["tcp_port"]))
        else:
            self._message("Added %s:%d" % (address, device["tcp_port"]))

    def _export_devices(self):
        devices = self.model.devices()
        if not devices:
            self._message("Nothing to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export devices", "devices.csv", "CSV files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(devices_to_csv(devices))
        except OSError as error:
            self._message("Export failed: %s" % error)
            return
        self._message("Exported %d device(s) to %s" % (len(devices), path))

    def _copy_rtsp(self):
        device = self._target_device()
        if device is None:
            self._message("Select or check a device first.")
            return
        if not device.get("ip"):
            self._message("RTSP needs a direct IP address.")
            return
        username, password = self._device_credentials(device)
        url = build_rtsp_url(
            device, username, password, self._channel(), self._stream())
        QApplication.clipboard().setText(url)
        if QDesktopServices.openUrl(QUrl(url)):
            self._message("RTSP opened (URL also copied): %s" % url)
        else:
            self._message("RTSP URL copied (no RTSP app available): %s" % url)

    def _toggle_video(self):
        if self.video_panel.is_active():
            self._stop_video()
            return
        device = self._target_device()
        if device is None:
            self._message("Select or check a device first.")
            return
        if not VideoPanel.available():
            self._message("No video decoder is available.")
            return
        username, password = self._device_credentials(device)
        stream = "Sub" if self._stream() else "Main"
        started = self.video_panel.start(
            device, username, password, stream=stream,
            channel=max(0, self._channel() - 1))
        if not started:
            return
        self._video_device = device
        self._video_credentials = (username, password)
        self.table_stack.setCurrentWidget(self.video_panel)
        self.video_button.setText("STOP VIDEO")
        self.middle_stack.setCurrentWidget(self.video_status_label)
        self._message("NETIP video: %s" % (
            device.get("cloud_id") or device.get("ip") or ""))

    def _stop_video(self):
        self._video_device = None
        self.video_panel.stop()
        self.table_stack.setCurrentWidget(self.table)
        self.video_button.setText("START VIDEO")
        self.video_status_label.setText("")
        self.middle_stack.setCurrentWidget(self.status_label)
        self._message("Video stopped")

    def _video_source_changed(self, *_):
        if not self.video_panel.is_active() or self._video_device is None:
            return
        stream = "Sub" if self._stream() else "Main"
        self.video_panel.switch(stream, max(0, self._channel() - 1))
        self._message("NETIP video: %s, %s" % (stream, self.channel_combo.currentText()))

    def _open_snapshot(self):
        device = self._target_device()
        if device is None:
            self._message("Select or check a device first.")
            return
        channel = max(0, self._channel() - 1)
        self._start_system_action(
            "snapshot", changes={"channel": channel},
            label="Taking snapshot on", device=device,
            on_fetched=self._on_snapshot)

    def _on_snapshot(self, payload):
        data = payload.get("snapshot") if isinstance(payload, dict) else None
        if not isinstance(data, (bytes, bytearray)) or not data:
            self._message("No snapshot returned.")
            return
        image = QImage.fromData(bytes(data), "JPG")
        if image.isNull():
            self._message("Snapshot is not a valid image.")
            return
        device = self._target_device() or {}
        address = str(device.get("ip") or "device").replace(".", "-")
        filename = "snap_%s_ch%d_%s.jpg" % (
            address, self._channel(), time.strftime("%Y%m%d-%H%M%S"))
        window = SnapshotWindow(
            image, bytes(data), filename, self)
        self._snapshot_windows.append(window)
        window.finished.connect(
            lambda _=0, w=window: self._snapshot_windows.remove(w)
            if w in self._snapshot_windows else None)
        window.show()
        self._message("Snapshot opened: %dx%d" % (image.width(), image.height()))

    NUMBER_ATTEMPTS = 2

    def _number_devices(self):
        if self._number_active or self._ipset_thread is not None:
            self._message("Another operation is running.")
            return
        devices = self.model.checked_devices()
        if not devices:
            self._message("Check at least one device first.")
            return
        base = self.initial_ip_edit.value()
        if not base:
            self._message("Set a valid Initial IP first.")
            return
        base_value = int(ipaddress.IPv4Address(base))
        jobs = []
        for offset, device in enumerate(devices):
            value = base_value + offset
            if value > 0xFFFFFFFF:
                break
            jobs.append((device, str(ipaddress.IPv4Address(value))))
        if not jobs:
            self._message("Initial IP plus device count exceeds 255.255.255.255.")
            return
        interface = self.interface_combo.currentData() or {}
        self._pause_search()
        self._number_queue = jobs
        self._number_total = len(jobs)
        self._number_done = 0
        self._number_failed = 0
        self._number_attempts = {}
        self._number_device_map = {
            DeviceTableModel.identity(device): device for device, _ip in jobs}
        self.model.clear_provision_states()
        for device, _ip in jobs:
            self.model.set_provision_state(
                DeviceTableModel.identity(device), "active")
        self._number_active = True
        self._number_interface = interface
        self.number_button.setEnabled(False)
        self._message("Numbering %d device(s) from %s ..." % (self._number_total, base))
        self._start_next_number_job()

    def _start_next_number_job(self):
        if not self._number_queue:
            self._number_active = False
            self.number_button.setEnabled(True)
            self._message(
                "Numbering done: %d ok, %d failed." % (self._number_done, self._number_failed))
            self._resume_search()
            return
        device, new_ip = self._number_queue.pop(0)
        identity = DeviceTableModel.identity(device)
        self._number_attempts[identity] = self._number_attempts.get(identity, 0) + 1
        self.model.set_provision_state(identity, "active")
        interface = self._number_interface or {}
        username, password = self._device_credentials(device)
        thread = IpSetThread(
            device, new_ip,
            device.get("subnet") or self.network_submask_edit.value(),
            device.get("gateway") or self.network_gateway_edit.value(),
            username,
            password,
            self.new_password_edit.text(),
            interface.get("ip", ""),
            interface.get("broadcast", "255.255.255.255"),
            http_port=device.get("http_port"),
            tcp_port=device.get("tcp_port"),
            parent=self)
        thread.result.connect(
            lambda message, ip=new_ip, ident=identity:
            self._on_number_result(ident, ip, message))
        thread.failed.connect(
            lambda text, ip=new_ip, ident=identity:
            self._on_number_failed(ident, ip, text))
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_number_finished)
        self._ipset_thread = thread
        thread.start()

    def _on_number_result(self, identity, ip, message):
        if message.get("Ret") == 100:
            self._number_done += 1
            device = self._number_device_map.get(identity)
            if device is not None:
                identity = self.model.set_device_ip(device, ip)
            self.model.set_provision_state(identity, "ok")
            self._message("Numbering %s: OK" % ip)
        else:
            self._number_retry(identity, ip, "Ret=%s" % message.get("Ret"))

    def _on_number_failed(self, identity, ip, text):
        self._number_retry(identity, ip, text)

    def _number_retry(self, identity, ip, reason):
        attempts = self._number_attempts.get(identity, 0)
        if attempts < self.NUMBER_ATTEMPTS:
            device = self._number_device_map.get(identity)
            if device is not None:
                self._number_queue.append((device, ip))
            self._message("Numbering %s failed (%s) — retry %d/%d ..." % (
                ip, reason, attempts + 1, self.NUMBER_ATTEMPTS))
        else:
            self._number_failed += 1
            self.model.set_provision_state(identity, "failed")
            self._message("Numbering %s failed: %s" % (ip, reason))

    def _on_number_finished(self):
        self._ipset_thread = None
        self._start_next_number_job()

    def _change_passwords(self):
        if self._pass_active or self._pass_thread is not None:
            self._message("Another operation is running.")
            return
        new_password = self.new_password_edit.text()
        devices = self.model.checked_devices()
        if not devices:
            device = self._selected_device()
            devices = [device] if isinstance(device, dict) else []
        if not devices:
            self._message("Check at least one device first.")
            return
        if not new_password:
            answer = QMessageBox.question(
                self, "Change password",
                "The new password is empty. Remove the password on %d device(s)?" % len(devices))
            if answer != QMessageBox.StandardButton.Yes:
                return
        self._pause_search()
        self._pass_queue = list(devices)
        self._pass_total = len(devices)
        self._pass_done = 0
        self._pass_failed = 0
        self._pass_active = True
        self.change_button.setEnabled(False)
        for device in devices:
            self.model.set_provision_state(
                DeviceTableModel.identity(device), "active")
        self._message("Changing password on %d device(s) ..." % self._pass_total)
        self._start_next_password_job()

    def _start_next_password_job(self):
        if not self._pass_queue:
            self._pass_active = False
            self.change_button.setEnabled(True)
            self._message("Password change done: %d ok, %d failed." % (
                self._pass_done, self._pass_failed))
            self._resume_search()
            return
        device = self._pass_queue.pop(0)
        identity = DeviceTableModel.identity(device)
        self.model.set_provision_state(identity, "active")
        username, password = self._device_credentials(device)
        thread = NetipThread(
            "user_password",
            device.get("ip") or "",
            username,
            password,
            cloud_id=device.get("cloud_id") or "",
            rps=bool(device.get("rps", True)),
            changes={"values": {
                "name": username,
                "old": password,
                "new": self.new_password_edit.text()}},
            port=int(device.get("tcp_port") or 34567),
            parent=self,
            no_md5=bool(device.get("no_md5")))
        thread.applied.connect(
            lambda payload, dev=device: self._on_password_result(dev, payload))
        thread.failed.connect(
            lambda text, dev=device: self._on_password_failed(dev, text))
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_password_finished)
        self._pass_thread = thread
        thread.start()

    def _on_password_result(self, device, payload):
        reply = payload.get("user_password") if isinstance(payload, dict) else None
        ret = reply.get("Ret") if isinstance(reply, dict) else None
        identity = DeviceTableModel.identity(device)
        label = device.get("ip") or identity
        if ret == 100:
            self._pass_done += 1
            device["password"] = self.new_password_edit.text()
            self.model.upsert(device)
            self.model.set_provision_state(identity, "ok")
            self._message("Password changed on %s" % label)
        else:
            self._pass_failed += 1
            self.model.set_provision_state(identity, "failed")
            self._message("Password change on %s failed: Ret=%s" % (label, ret))

    def _on_password_failed(self, device, text):
        identity = DeviceTableModel.identity(device)
        self._pass_failed += 1
        self.model.set_provision_state(identity, "failed")
        self._message("Password change on %s failed: %s" % (
            device.get("ip") or identity, text))

    def _on_password_finished(self):
        self._pass_thread = None
        self._start_next_password_job()

    def _network_config_changes(self):
        changes = {}
        dns1 = self.network_dns1_edit.value()
        dns2 = self.network_dns2_edit.value()
        if dns1 and dns2:
            changes["dns"] = {
                "Address": format_ip_set(dns1),
                "SpareAddress": format_ip_set(dns2),
            }
        if self._network_dhcp_config:
            dhcp = [dict(entry) for entry in self._network_dhcp_config
                    if isinstance(entry, dict)]
            for entry in dhcp:
                entry["Enable"] = self.network_dhcp_check.isChecked()
            if dhcp:
                changes["dhcp"] = dhcp
        changes["adaptive"] = {"IPAdaptive": self.network_adaptive_check.isChecked()}
        changes["smartnet"] = {
            "Enable": self.network_smartnet_auto_check.isChecked(),
            "bChangeIP": self.network_smartnet_change_ip_check.isChecked(),
        }
        changes["project_mode"] = not self.network_smartnet_check.isChecked()
        if self._network_wifi_config:
            wifi = dict(self._network_wifi_config)
            wifi["Enable"] = 1 if self.wifi_group.isChecked() else 0
            wifi["SSID"] = self.network_wifi_ssid_edit.currentText().strip()
            wifi["Keys"] = self.network_wifi_password_edit.text()
            wifi["Auth"] = self.network_wifi_auth_combo.currentText()
            wifi["EncrypType"] = self.network_wifi_encrypt_combo.currentText()
            wifi["NetType"] = self.network_wifi_nettype_combo.currentText()
            changes["wifi"] = wifi
        if self._network_rtsp_config:
            rtsp = dict(self._network_rtsp_config)
            server = dict(rtsp.get("Server") or {})
            server["Port"] = port_value(self.network_rtsp_edit, 554)
            rtsp["Server"] = server
            changes["rtsp"] = rtsp
        if self._network_upgrade_config:
            upgrade = dict(self._network_upgrade_config)
            upgrade["Enable"] = self.upgrade_group.isChecked()
            upgrade["ServerAddr"] = self.network_upgrade_server_edit.text().strip()
            upgrade["ServerPort"] = port_value(self.network_upgrade_port_edit, 8083)
            upgrade["AutoCheck"] = 1 if self.network_upgrade_autocheck_check.isChecked() else 0
            upgrade["AutoUpgradeImp"] = 1 if self.network_upgrade_autoimp_check.isChecked() else 0
            upgrade["IgnoreAllVersion"] = 1 if self.network_upgrade_ignore_all_check.isChecked() else 0
            upgrade["IgnoreCurTime"] = 1 if self.network_upgrade_ignore_time_check.isChecked() else 0
            upgrade["IgnoreCurVersion"] = 1 if self.network_upgrade_ignore_version_check.isChecked() else 0
            upgrade["JustImpVersion"] = 1 if self.network_upgrade_just_imp_check.isChecked() else 0
            changes["upgrade"] = upgrade
        if self._network_upnp_config:
            upnp = dict(self._network_upnp_config)
            upnp["Enable"] = self.network_upnp_check.isChecked()
            changes["upnp"] = upnp
        if self._network_onvif_pwd_config:
            onvif = dict(self._network_onvif_pwd_config)
            onvif["Enable"] = self.network_onvif_pwd_check.isChecked()
            changes["onvif_pwd"] = onvif
        if self._network_pms_config:
            pms = dict(self._network_pms_config)
            pms["Enable"] = self.network_pms_check.isChecked()
            changes["pms"] = pms
        if self._network_ntp_config:
            ntp = dict(self._network_ntp_config)
            ntp["Enable"] = self.ntp_group.isChecked()
            manual = self.network_ntp_manual_radio.isChecked()
            ntp["TimeZone"] = 13 if manual else 14
            server = dict(ntp.get("Server") or {})
            if manual:
                server["Name"] = self.network_ntp_server_edit.text().strip()
            ntp["Server"] = server
            ntp["UpdatePeriod"] = port_value(self.network_ntp_period_edit, 60)
            changes["ntp"] = ntp
        pubcfg = self.network_pubcfg_edit.text().strip()
        if pubcfg:
            changes["pubcfg"] = {"NetPub-Cfg": pubcfg}
        caps = self.network_caps_edit.text().strip()
        if caps:
            changes["caps"] = {"NetCaps": caps}
        changes["force_dhcp"] = {"Enable": self.network_force_dhcp_check.isChecked()}
        if self._network_ability_config:
            ability = dict(self._network_ability_config)
            ability["VNICFunctionEnable"] = self.network_vnic_check.isChecked()
            changes["ability"] = ability
        if self._network_oemcfg_config:
            oemcfg = dict(self._network_oemcfg_config)
            oemcfg["Port"] = port_value(self.network_onvif_edit, 8899)
            changes["oemcfg"] = oemcfg

        if self._network_disable_conn_config:
            disable_conn = {}
            for key, check in self._disable_conn_checks.items():
                if not check.isEnabled():
                    continue
                original = self._network_disable_conn_config.get(key)
                if isinstance(original, str):
                    disable_conn[key] = "true" if check.isChecked() else "false"
                else:
                    disable_conn[key] = check.isChecked()
            if disable_conn:
                changes["disable_xm_server"] = disable_conn
        if self._network_nat_config:
            nat = dict(self._network_nat_config)
            nat["NatEnable"] = self.nat_group.isChecked()
            nat["Addr"] = self.network_nat_addr_edit.text().strip()
            dns1 = self.network_nat_dns1_edit.value()
            dns2 = self.network_nat_dns2_edit.value()
            if dns1:
                nat["DnsServer1"] = format_ip_set(dns1)
            if dns2:
                nat["DnsServer2"] = format_ip_set(dns2)
            nat["Port"] = port_value(self.network_nat_port_edit, 8000)
            nat["XMeyeMTU"] = port_value(self.network_nat_mtu_edit, 1280)
            changes["nat"] = nat
        return changes

    def _apply_network(self):
        if (self._number_active or self._ipset_thread is not None
                or self._network_thread is not None):
            self._message("Another operation is running.")
            return
        device = self._target_device()
        if not isinstance(device, dict):
            self._message("No device selected — pick a table row first.")
            return
        try:
            address = str(ipaddress.IPv4Address(self.network_address_edit.value()))
            submask = str(ipaddress.IPv4Address(self.network_submask_edit.value()))
            gateway = str(ipaddress.IPv4Address(self.network_gateway_edit.value()))
        except (ipaddress.AddressValueError, ValueError):
            self._message("Invalid IP address, subnet mask or gateway.")
            return
        raw = device.get("raw") or {}
        raw["TransferPlan"] = self.network_transfer_combo.currentText().strip()
        raw["UseHSDownLoad"] = self.network_hsdownload_check.isChecked()
        device["raw"] = raw
        self._pause_search()
        self._pending_network = (device, address, submask, gateway)
        username, password = self._device_credentials(device)
        thread = NetipThread(
            "network_config", device.get("ip") or "",
            username, password,
            cloud_id=device.get("cloud_id") or "",
            rps=bool(device.get("rps", True)),
            changes=self._network_config_changes(),
            port=device.get("tcp_port") or 34567,
            parent=self,
            no_md5=bool(device.get("no_md5")))
        thread.applied.connect(self._on_network_config_applied)
        thread.failed.connect(self._on_network_config_failed)
        thread.finished.connect(self._on_network_config_finished)
        self._network_thread = thread
        self._message("Applying network settings on %s ..." % (device.get("ip") or ""))
        thread.start()

    def _on_network_config_applied(self, results):
        summary = []
        for name, reply in results.items():
            ret = reply.get("Ret") if isinstance(reply, dict) else None
            summary.append("%s Ret=%s" % (name, ret))
        self._message("Network config: " + (", ".join(summary) if summary else "nothing to set"))

    def _on_network_config_failed(self, text):
        self._message("Network config failed: %s" % text)

    def _on_network_config_finished(self):
        thread = self._network_thread
        self._network_thread = None
        if thread is not None:
            thread.deleteLater()
        pending = self._pending_network
        self._pending_network = None
        if pending is None:
            self._resume_search()
            return
        device, address, submask, gateway = pending
        self._ipset_target = (device, address)
        interface = self.interface_combo.currentData()
        if not isinstance(interface, dict):
            interface = {"ip": "", "broadcast": "255.255.255.255"}
        self._message(
            "Applying %s / %s / %s, HTTP %d, TCP %d via %s ..." % (
                address, submask, gateway,
                port_value(self.network_http_edit, 80), port_value(self.network_tcp_edit, 34567),
                interface.get("broadcast") or "255.255.255.255"))
        username, password = self._device_credentials(device)
        thread = IpSetThread(
            device, address, submask, gateway,
            username,
            password,
            self.new_password_edit.text(),
            interface.get("ip", ""),
            interface.get("broadcast", "255.255.255.255"),
            http_port=port_value(self.network_http_edit, 80),
            tcp_port=port_value(self.network_tcp_edit, 34567),
            host_name=self.network_name_edit.text().strip() or None,
            parent=self,
        )
        thread.result.connect(self._on_network_result)
        thread.failed.connect(self._on_network_failed)
        thread.finished.connect(self._on_network_finished)
        self._ipset_thread = thread
        thread.start()

    def _on_network_result(self, message):
        ret = message.get("Ret")
        text = RESULT_CODES.get(ret, "Unknown result")
        self._message("Device replied: Ret=%s (%s)" % (ret, text))
        target = self._ipset_target
        self._ipset_target = None
        if ret != 100 or target is None:
            return
        device, address = target
        old_address = str(device.get("ip") or "")
        if not address or address == old_address:
            return
        identity = DeviceTableModel.identity(device)
        if identity == self._connected_identity:
            if self.video_panel.is_active():
                self._stop_video()
            self._drop_connection(
                "IP changed to %s — reconnect to the new address" % address)
        self.model.set_device_ip(device, address)

    def _on_network_failed(self, text):
        self._message("Failed: %s" % text)

    def _on_network_finished(self):
        thread = self._ipset_thread
        self._ipset_thread = None
        if thread is not None:
            thread.deleteLater()
        self._resume_search()

    def _on_failed(self, message):
        self._status_text = "Error: %s" % message
        self.status_label.setText(self._refresh_status_text())
        if self.search_button.isChecked():
            self.search_button.setChecked(False)

    def closeEvent(self, event):
        self._stop_session()
        channels_dialog = self._channels_dialog
        self._channels_dialog = None
        if channels_dialog is not None:
            channels_dialog.close()
            channels_dialog.deleteLater()
        self.video_panel.stop(wait=True)
        thread = self._thread
        self._thread = None
        if thread is not None:
            thread.stop()
            thread.wait(3000)
        ipset_thread = self._ipset_thread
        self._ipset_thread = None
        if ipset_thread is not None:
            ipset_thread.wait(4000)
        pass_thread = self._pass_thread
        self._pass_thread = None
        if pass_thread is not None:
            pass_thread.wait(10000)
        probe_thread = self._probe_thread
        self._probe_thread = None
        if probe_thread is not None:
            probe_thread.wait(4000)
        release_thread = self._release_thread
        self._release_thread = None
        if release_thread is not None:
            release_thread.wait(6000)
        netip_thread = self._netip_thread
        self._netip_thread = None
        if netip_thread is not None:
            netip_thread.wait(10000)
        for stale in list(self._stale_threads):
            stale.wait(10000)
        self._stale_threads = []
        network_thread = self._network_thread
        self._network_thread = None
        if network_thread is not None:
            network_thread.wait(10000)
        super().closeEvent(event)


def fit_window_to_screen(window):
    """Keep the title bar reachable when the layout minimum exceeds the screen."""
    screen = window.screen() or QApplication.primaryScreen()
    if screen is None:
        return
    available = screen.availableGeometry()
    frame = window.frameGeometry()
    width = max(1, frame.width())
    height = max(1, frame.height())
    x = frame.x()
    y = frame.y()
    if x < available.left() or x + width > available.right() + 1:
        x = available.left() + max(0, (available.width() - width) // 2)
    if y < available.top() or y + height > available.bottom() + 1:
        y = available.top() + max(0, (available.height() - height) // 2)
    x = max(available.left(), x)
    y = max(available.top(), y)
    if (x, y) != (frame.x(), frame.y()):
        window.move(x, y)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("XMDMS")
    app.setWindowIcon(app_icon())
    settings = QSettings("xmdm3", "xmdms")
    load_language()
    retranslate_filter = RetranslateFilter(app)
    app.installEventFilter(retranslate_filter)
    apply_theme(app, settings.value("theme", "auto"))
    install_query_logger()
    window = MainWindow()
    icon = app_icon()
    window.setWindowIcon(icon)
    app.setWindowIcon(icon)
    fit_window_to_screen(window)
    window.show()
    fit_window_to_screen(window)
    QTimer.singleShot(0, lambda: fit_window_to_screen(window))
    window.setWindowIcon(icon)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
