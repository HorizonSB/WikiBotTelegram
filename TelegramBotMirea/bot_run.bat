@echo off

call %~dp0TelegramBotMirea\venv\Scripts\activate

set TOKEN=

cd %~dp0TelegramBotMirea

python bot_telegram.py

pause 