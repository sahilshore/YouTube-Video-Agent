$ErrorActionPreference = "Stop"
if (-not (Test-Path ".venv\Scripts\python.exe")) { throw "Virtual environment missing. Run .\setup.ps1 first." }
& ".venv\Scripts\python.exe" -m streamlit run app.py --server.address localhost --server.port 8501

