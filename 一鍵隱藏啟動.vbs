Set WshShell = CreateObject("WScript.Shell")

' 1. 在完全隱藏視窗的狀態下啟動 FastAPI 伺服器
WshShell.Run "cmd /c .\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000", 0, False

' 等待 1 秒讓伺服器就緒
WScript.Sleep 1000

' 2. 在完全隱藏視窗的狀態下啟動 ngrok 穿透
WshShell.Run "cmd /c ""C:\Users\yangh\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe"" http 8000", 0, False
