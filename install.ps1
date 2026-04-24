# Refuos - Installer (Windows)
# Usage: irm https://raw.githubusercontent.com/heavybeard/refuos/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$Repo = "heavybeard/refuos"
$BaseUrl = "https://github.com/$Repo/releases/latest/download"
$Packages = @("refuos-italiano.yml", "refuos-accenti.yml", "refuos-dev.yml")

Write-Host ""
Write-Host "Refuos - Installer"
Write-Host "=================="
Write-Host ""

# 1. Check/install Espanso
if (-not (Get-Command espanso -ErrorAction SilentlyContinue)) {
    Write-Host "Espanso not found."
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Installing Espanso via winget..."
        winget install espanso.espanso
    } else {
        Write-Host "Error: winget not available."
        Write-Host "Download and install Espanso manually from: https://espanso.org/install/win/"
        exit 1
    }
    Write-Host ""
    Write-Host "Note: Windows may ask you to authorize Espanso."
    Write-Host "Accept the request, then press Enter to continue."
    Read-Host "Press Enter to continue"
    espanso service register
    espanso start
} else {
    Write-Host "Espanso already installed"
}

# 2. Find Espanso match directory
$EspansoConfig = (espanso path config).Trim()
$MatchDir = Join-Path $EspansoConfig "match"
New-Item -ItemType Directory -Force -Path $MatchDir | Out-Null

# 3. Download pre-built rules (no Python, no Git required)
Write-Host "Downloading Refuos rules..."
Write-Host ""
foreach ($pkg in $Packages) {
    $url = "$BaseUrl/$pkg"
    $dest = Join-Path $MatchDir $pkg
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
    Write-Host "  ok  $pkg"
}

# 4. Restart Espanso
espanso restart

Write-Host ""
Write-Host "Refuos installed. 3 packages:"
Write-Host "   refuos-italiano.yml  - everyday Italian words"
Write-Host "   refuos-accenti.yml   - accents and future tense"
Write-Host "   refuos-dev.yml       - tech/code terms"
Write-Host ""
Write-Host "   Try typing 'perche' in any app - it becomes 'perche''"
Write-Host "   To remove a package: delete its .yml file from:"
Write-Host "   $MatchDir"
Write-Host ""
Write-Host "   To update: re-run this installer at any time"
Write-Host ""
