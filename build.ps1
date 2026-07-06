#Requires -Version 5.1
<#
.SYNOPSIS
    Builds IdleAssistant.exe with PyInstaller (Windows, onefile).
.EXAMPLE
    .\build.ps1
    .\build.ps1 -Clean
#>
param(
    [switch]$Clean
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
Set-Location -LiteralPath $root

$script  = Join-Path $root 'IdleAssistant.pyw'
$icon    = Join-Path $root 'icon.ico'
$outDir  = Join-Path $root 'dist_windows'

if (-not (Test-Path -LiteralPath $script)) { throw "Not found: $script" }
if (-not (Test-Path -LiteralPath $icon))   { throw "Not found: $icon" }

Write-Host '==> Installing dependencies' -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install pyinstaller pyautogui keyboard pystray pillow

if ($Clean) {
    Write-Host '==> Cleaning build artifacts' -ForegroundColor Cyan
    foreach ($p in @('build', 'dist', 'IdleAssistant.spec')) {
        $full = Join-Path $root $p
        if (Test-Path -LiteralPath $full) { Remove-Item -LiteralPath $full -Recurse -Force }
    }
}

Write-Host '==> Building exe' -ForegroundColor Cyan
python -m PyInstaller `
    --noconfirm `
    --onefile `
    --noconsole `
    --name IdleAssistant `
    --icon $icon `
    --add-data "$icon;." `
    $script

$built = Join-Path $root 'dist\IdleAssistant.exe'
if (-not (Test-Path -LiteralPath $built)) { throw "Build failed: $built not found" }

New-Item -ItemType Directory -Path $outDir -Force | Out-Null
Copy-Item -LiteralPath $built -Destination (Join-Path $outDir 'IdleAssistant.exe') -Force

Write-Host "==> Done: $(Join-Path $outDir 'IdleAssistant.exe')" -ForegroundColor Green
