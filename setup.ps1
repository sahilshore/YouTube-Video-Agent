$ErrorActionPreference = "Stop"

Write-Host "Setting up YOUTUBE VIDEO AGENT" -ForegroundColor Cyan
$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $python) { throw "Python 3.11+ is required. Install Python and rerun setup.ps1." }

& $python.Source -c "import sys; assert sys.version_info >= (3,11), 'Python 3.11+ is required'; print(sys.version)"
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    & $python.Source -m venv .venv
}
$venvPython = (Resolve-Path ".venv\Scripts\python.exe").Path
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

New-Item -ItemType Directory -Force -Path "storage\projects", "resources\fonts", "resources\music", "resources\images" | Out-Null
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) { Copy-Item ".env.example" ".env" }

if (Get-Command ffmpeg -ErrorAction SilentlyContinue) { Write-Host "FFmpeg: available" -ForegroundColor Green } else { Write-Warning "FFmpeg was not found on PATH. Install it or set FFMPEG_PATH in .env." }
if (Get-Command ffprobe -ErrorAction SilentlyContinue) { Write-Host "FFprobe: available" -ForegroundColor Green } else { Write-Warning "FFprobe was not found on PATH. Install it or set FFPROBE_PATH in .env." }
Write-Host "Setup complete. Add provider keys to .env, then run .\run.ps1" -ForegroundColor Green

