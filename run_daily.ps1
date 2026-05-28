$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python -m src.main run --date (Get-Date -Format "yyyy-MM-dd")

