@echo off
setlocal
cd /d "%~dp0"

if not exist .build (
    py -3.12 -m venv .build || goto :error
)
call .build\Scripts\activate.bat || goto :error

python -m pip install --upgrade pip || goto :error
pip install -r requirements.txt pyinstaller || goto :error
python tools\make_icon.py || goto :error
pyinstaller --noconfirm xmdms.spec || goto :error

echo.
echo Built: dist\xmdms\xmdms.exe
exit /b 0

:error
echo.
echo Build failed.
exit /b 1
