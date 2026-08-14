# Touhou Universalis II — one-click validation launcher
# Usage:  .\tools\run_validate.ps1 [--changed] [--ai-report] [<target-path>]
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$script = Join-Path $PSScriptRoot 'th_validate.py'
& python $script @args
exit $LASTEXITCODE
