@echo off
setlocal
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment missing. Run setup.ps1 first.
  exit /b 1
)
".venv\Scripts\python.exe" -m streamlit run app.py --server.address localhost --server.port 8501

