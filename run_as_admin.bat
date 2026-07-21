@echo off
REM ============================================================
REM  Chay Plaxis Hotkey Tool voi quyen Administrator.
REM  Thu vien 'keyboard' can quyen admin de bat phim tat toan cuc.
REM  Nhap dup file nay -> UAC hoi quyen -> chon Yes.
REM ============================================================

cd /d "%~dp0"

REM Mo mot Command Prompt moi voi quyen Administrator, chay python run.py
powershell -NoProfile -Command ^
  "Start-Process -FilePath 'cmd.exe' -ArgumentList '/k cd /d \"%~dp0\" ^&^& python run.py' -Verb RunAs"
