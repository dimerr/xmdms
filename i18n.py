"""Minimal English/Russian localisation for xmdms.

English is the source language and the fallback.  Only exact UI strings are
translated here; missing strings deliberately stay in English.
"""

from PySide6.QtCore import QLocale, QSettings

LANGUAGE_SETTING = "language"
SUPPORTED_LANGUAGES = ("auto", "en", "ru")

_current = "en"

RU = {
    # Common / main window
    "Search": "Поиск",
    "Stop": "Стоп",
    "Add": "Добавить",
    "Export": "Экспорт",
    "SNAP": "Снимок",
    "START VIDEO": "ВИДЕО",
    "Focus": "Фокус",
    "Show focus sharpness scores for four regions. Point the camera at a detailed scene.":
        "Показать оценку резкости по четырём зонам. Наведите камеру на детализированную сцену.",
    "Analyzing focus...": "Анализ фокуса...",
    "Low detail — use a target": "Мало деталей — используйте мишень",
    "Channel:": "Канал:",
    "Stream:": "Поток:",
    "Main": "Основной",
    "Sub": "Доп.",
    "Save": "Сохранить",
    "Console": "Консоль",
    "User:": "Пользователь:",
    "Password:": "Пароль:",
    "New password:": "Новый пароль:",
    "Change": "Сменить",
    "Start IP:": "Начальный IP:",
    "Provision": "Назначить",
    "Interface:": "Интерфейс:",
    "Connected": "Подключено",
    "Disconnected": "Отключено",
    "Stopped": "Остановлено",
    "Idle": "Ожидание",
    "device(s)": "устройств",
    "Version": "Версия",
    "Build Date": "Дата сборки",
    "Host Name": "Имя хоста",
    "Name": "Имя",
    "Type": "Тип",
    "Status": "Статус",
    "Group": "Группа",
    "OK": "ОК",
    "Cancel": "Отмена",
    "Yes": "Да",
    "No": "Нет",
    "Apply": "Применить",
    "Close": "Закрыть",
    "Copy": "Копировать",
    "Refresh": "Обновить",
    "Default": "По умолчанию",
    "Show": "Показывать",
    "No device selected — pick a table row first.":
        "Устройство не выбрано — выберите строку в таблице.",
    "Hide": "Скрывать",
    "Auto": "Авто",
    "Light": "Светлая",
    "Dark": "Тёмная",
    "English": "Английский",
    "Russian": "Русский",

    # Tabs
    "Network": "Сеть",
    "System": "Система",
    "Display": "Дисплей",
    "Encode": "Кодирование",
    "Camera": "Камера",
    "Storage": "Хранилище",
    "Users": "Пользователи",
    "Settings": "Настройки",
    "About": "О программе",
    "Check for updates": "Проверить обновления",
    "Not checked": "Не проверялось",
    "Checking for updates...": "Проверка обновлений...",
    "No release notes.": "Нет списка изменений.",
    "No commit message.": "Нет сообщения коммита.",
    "current": "текущая",
    "Update available:": "Доступно обновление:",
    "Up to date — latest": "Обновлений нет — последний",
    "Up to date — latest commit": "Обновлений нет — последний коммит",
    "New commits available on": "Новые коммиты в",
    "Latest commit:": "Последний коммит:",
    "GitHub API rate limit reached": "Достигнут лимит запросов GitHub API",
    "No releases or commits found": "Релизы или коммиты не найдены",

    # Network
    "LAN": "LAN",
    "Name:": "Имя:",
    "IP:": "IP:",
    "Subnet:": "Маска:",
    "Gateway:": "Шлюз:",
    "DNS 1:": "DNS 1:",
    "DNS 2:": "DNS 2:",
    "Quality": "Качество",
    "Default IP": "IP по умолч.",
    "Default DNS": "DNS по умолч.",
    "IP adaptive": "Адаптив. IP",
    "Change IP": "Сменить IP",
    "Auto connect": "Автоподкл.",
    "UseHSDownLoad": "Быстрое скач.",
    "Addr:": "Адрес:",
    "Port:": "Порт:",
    "Period:": "Период:",
    "Manual": "Вручную",
    "Server:": "Сервер:",
    "Cloud upgrade": "Облачн. обновл.",
    "Upgrade": "Обновление",
    "Auto check": "Автопров.",
    "Auto upgrade": "Автообновл.",
    "Ignore all ver": "Все версии",
    "Ignore cur time": "Игнор. вр.",
    "Ignore cur ver": "Игнор. вер.",
    "Just imp ver": "Важные",
    "SSID:": "SSID:",
    "Pass:": "Пароль:",
    "Scan": "Поиск",
    "Sec:": "Защита:",
    "Enc:": "Шифр.:",
    "Net:": "Сеть:",

    # System
    "Info": "Информация",
    "General": "Общие",
    "Hardware:": "Оборудование:",
    "Cloud ID:": "Cloud ID:",
    "Software:": "ПО:",
    "Build time:": "Сборка:",
    "Age": "В работе",
    "Channels:": "Каналы:",
    "Type:": "Тип:",
    "NAT status:": "Статус NAT:",
    "NAT info:": "Инфо NAT:",
    "TV standard:": "ТВ стандарт:",
    "Language:": "Язык:",
    "Restart day:": "День перез.:",
    "Hour:": "Час:",
    "Time zone:": "Часовой пояс:",
    "Date format:": "Формат даты:",
    "Separator:": "Разделитель:",
    "Format:": "Формат:",
    "MaxChannels:": "Макс. кан.:",
    "Beeper": "Сигнал",
    "Face function": "Функция лиц",
    "Enable debug": "Отладка",
    "AudioIn:": "AudioIn:",
    "Sync time": "Синхр. времени",
    "Digital channels": "Цифровые каналы",
    "Reboot": "Перезагрузка",
    "Import config": "Импорт настроек",
    "Export config": "Экспорт настроек",
    "Reset config": "Сброс настроек",
    "View logs": "Просмотр логов",
    "Erase logs": "Очистить логи",
    "Recovery": "Восстановление",
    "Dump": "Дамп",
    "Open dir": "Открыть папку",

    # Display
    "Video out": "Видеовыход",
    "Resolution:": "Разреш.:",
    "GUI set": "Интерфейс",
    "Window alpha:": "Прозрачность:",

    # Encode
    "All channels": "Все каналы",
    "Main stream": "Осн. поток",
    "Substream": "Доп. поток",
    "Compression:": "Сжатие:",
    "FPS:": "FPS:",
    "RC type:": "Тип RC:",
    "Quality:": "Качество:",
    "Bitrate:": "Битрейт:",
    "I-frame int:": "I-кадр:",
    "Enable:": "Включить:",
    "Video": "Видео",
    "Audio": "Аудио",
    "Smart encode:": "Умное кодир.:",
    "Channels": "Каналы",
    "Encode — all channels": "Кодирование — все каналы",
    "To all": "Всем",
    "M res": "Осн. разр.",
    "M FPS": "Осн. FPS",
    "M RC": "Осн. RC",
    "M quality": "Осн. кач.",
    "M I-frame": "Осн. I",
    "S res": "Доп. разр.",
    "S FPS": "Доп. FPS",
    "S RC": "Доп. RC",
    "S quality": "Доп. кач.",
    "S I-frame": "Доп. I",
    "Smart M": "Умн. осн.",
    "Smart S": "Умн. доп.",

    # Camera
    "Day/Night:": "День/ночь:",
    "White balance:": "Баланс белого:",
    "Aperture:": "Диафрагма:",
    "Exposure level:": "Экспозиция:",
    "Shutter:": "Затвор:",
    "Auto gain:": "Автоусиление:",
    "Gain:": "Усиление:",
    "Elec level:": "Эл. уровень:",
    "AE sensitivity:": "Чувств. AE:",
    "Day NF level:": "Шум днём:",
    "Night NF level:": "Шум ночью:",
    "IR-CUT mode:": "IR-CUT:",
    "DNC threshold:": "Порог DNC:",
    "DN switch:": "Перекл. DN:",
    "Style:": "Стиль:",
    "DWDR:": "DWDR:",
    "Strength:": "Сила:",
    "Flip": "Верт. отраж.",
    "Mirror": "Гориз. отраж.",
    "IR-CUT swap": "IR-CUT инв.",
    "Reject flicker": "Антимерц.",
    "White light": "Подсветка",
    "Work mode:": "Режим:",
    "Brightness:": "Яркость:",
    "Trigger level:": "Уровень:",
    "Trigger duration:": "Длительность:",
    "Period enable:": "Расписание:",
    "Start hour:": "Начало (ч):",
    "Start minute:": "Начало (мин):",
    "End hour:": "Конец (ч):",
    "End minute:": "Конец (мин):",

    # Storage
    "Disk": "Диск",
    "Capacity": "Объём",
    "Free": "Свободно",
    "Start": "Начало",
    "End": "Конец",
    "Read/Write": "Чтение/запись",
    "Read only": "Только чтение",
    "Redundant": "Резерв",
    "Snapshot": "Снимки",
    "Format": "Форматировать",
    "Recover": "Восстановить",

    # RS232 / PTZ
    "Function:": "Функция:",
    "Baud rate:": "Скорость:",
    "Data bits:": "Биты данных:",
    "Stop bits:": "Стоп-биты:",
    "Parity:": "Чётность:",
    "Protocol:": "Протокол:",
    "Address:": "Адрес:",

    # Users
    "Users:": "Пользователи:",
    "Groups:": "Группы:",
    "Add user": "Добавить",
    "Modify user": "Изменить",
    "Delete user": "Удалить",
    "Modify PW": "Сменить пароль",
    "Add group": "Добавить группу",
    "Modify group": "Изменить группу",
    "Delete group": "Удалить группу",
    "Reuseable": "Многоразовый",

    # Settings
    "Search timeout:": "Таймаут поиска:",
    "Probes per search: at least 3": "Попыток на поиск: не менее 3",
    "Search attempts:": "Попыток поиска:",
    "Theme:": "Тема:",
    "Passwords:": "Пароли:",

    # Dialogs / digital channels
    "Add device": "Добавить устройство",
    "IP address:": "IP-адрес:",
    "Subnet mask:": "Маска подсети:",
    "Login:": "Логин:",
    "Transport:": "Транспорт:",
    "Search type:": "Тип поиска:",
    "Provision IP": "Назначить IP",
    "Add all IPC": "Добавить все IPC",
    "Add to channels": "Добавить в каналы",
    "Change network settings...": "Изменить сетевые настройки...",
    "Save image...": "Сохранить изображение...",
    "Set": "Выбор",
    "Mask": "Маска",
    "Gateway": "Шлюз",
    "Port": "Порт",
    "Host Name": "Имя хоста",
    "Channels": "Каналы",
    "On": "Вкл",
    "Name": "Имя",
    "SyncRes": "Синхр.разр.",
    "SyncTime": "Время",
    "Prio": "Приор.",
    "Ch": "Кан.",
    "User": "Польз.",
    "Password": "Пароль",
    "CfgName": "Имя конфиг.",
    "Channel name:": "Имя канала:",
    "Sync res:": "Синхр. разр.:",
    "Sync time:": "Синхр. времени:",
    "Delay decode:": "Задержка:",
    "Subnet:": "Маска:",
    "Change password": "Сменить пароль",
    "Old password:": "Старый пароль:",
    "New password:": "Новый пароль:",
    "Reset config": "Сброс настроек",
    "Recovery image": "Образ восстановления",
    "Flash dump": "Дамп флеш-памяти",
}

PREFIXES = (
    ("Update check failed: ", "Ошибка проверки обновлений: "),
    ("GitHub API error: HTTP ", "Ошибка GitHub API: HTTP "),
    ("Network error: ", "Ошибка сети: "),
    ("Build date: ", "Дата сборки: "),
    ("Update available: ", "Доступно обновление: "),
    ("Up to date — latest commit", "Обновлений нет — последний коммит"),
    ("Up to date — latest", "Обновлений нет — последний"),
    ("New commits available on ", "Новые коммиты в "),
    ("Latest commit: ", "Последний коммит: "),
    ("Digital channels — ", "Цифровые каналы — "),
    ("Change password — ", "Сменить пароль — "),
    ("Network settings — ", "Сетевые настройки — "),
    ("Connected: ", "Подключено: "),
    ("NetIP error: ", "Ошибка NetIP: "),
    ("Connection lost: ", "Соединение потеряно: "),
    ("Connection lost", "Соединение потеряно"),
    ("Cannot connect to ", "Не удалось подключиться к "),
    ("Login failed", "Ошибка входа"),
    ("Wi-Fi scan: ", "Поиск Wi-Fi: "),
    ("Snapshot opened: ", "Снимок открыт: "),
    ("Snapshot saved: ", "Снимок сохранён: "),
    ("Search finished — ", "Поиск завершён — "),
)


def detected_language():
    try:
        name = QLocale.system().name().lower()
    except Exception:
        return "en"
    return "ru" if name.startswith("ru") else "en"


def resolve_language(setting):
    setting = str(setting or "auto").strip().lower()
    if setting in ("en", "ru"):
        return setting
    return detected_language()


def load_language():
    setting = str(
        QSettings("xmdm3", "xmdms").value(
            LANGUAGE_SETTING, "auto", type=str) or "auto").strip().lower()
    if setting not in SUPPORTED_LANGUAGES:
        setting = "auto"
    set_language(resolve_language(setting))
    return setting


def set_language(language):
    global _current
    _current = "ru" if str(language).strip().lower() == "ru" else "en"
    return _current


def current_language():
    return _current


def tr(text):
    text = "" if text is None else str(text)
    if _current != "ru" or not text:
        return text
    translated = RU.get(text)
    if translated is not None:
        return translated
    for source, target in PREFIXES:
        if text.startswith(source):
            return target + text[len(source):]
    return text
