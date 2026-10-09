@echo off
chcp 65001 >nul
echo 正在關閉 LINE Bot 與 ngrok 背景運行...
taskkill /F /IM ngrok.exe >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a >nul 2>&1
echo 已成功關閉所有背景服務！
timeout /t 2 >nul
