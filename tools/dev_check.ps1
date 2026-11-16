[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

# Fork-owned maintenance tools only. Does not build Rust or start the desktop app;
# the product's own gates are in CONTRIBUTING.md / TESTING.md (upstream).
Write-Host "==> pytest tests/fork"
python -m pytest tests/fork -q
if ($LASTEXITCODE -ne 0) { throw "pytest failed with exit code $LASTEXITCODE" }
Write-Host "OK"
