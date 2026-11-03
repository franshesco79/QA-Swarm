Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\frans\.gemini\antigravity\scratch\qa-swarm"

' Kill previous if running on 8090 and 8501
WshShell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -aon ^| findstr :8090') do taskkill /f /pid %a", 0, True
WshShell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -aon ^| findstr :8501') do taskkill /f /pid %a", 0, True

' Run HTTP server on 8090 totally hidden (SW_HIDE = 0, no Alt+Tab)
WshShell.Run """C:\Users\frans\.gemini\antigravity\scratch\qa-swarm\.venv\Scripts\python.exe"" -m http.server 8090 --directory test_samples", 0, False

' Run Streamlit on 8501 totally hidden (SW_HIDE = 0, no Alt+Tab)
WshShell.Run """C:\Users\frans\.gemini\antigravity\scratch\qa-swarm\.venv\Scripts\python.exe"" -m streamlit run app/main.py --server.port 8501 --server.headless true", 0, False

WScript.Sleep 3000
WshShell.Run "http://localhost:8501"
