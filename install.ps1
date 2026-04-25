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

# Verify Espanso version >= 2.0
$EspansoVersionStr = (espanso --version 2>&1) -replace '[^0-9.]', '' | Select-Object -First 1
$EspansoMajor = [int]($EspansoVersionStr -split '\.')[0]
if ($EspansoMajor -lt 2) {
    Write-Host "Error: Espanso 2.0 or later is required (found: $EspansoVersionStr)."
    Write-Host "Download the latest version from: https://espanso.org"
    exit 1
}

# 2. Find Espanso match directory
$EspansoConfig = (espanso path config).Trim()
$MatchDir = Join-Path $EspansoConfig "match"
New-Item -ItemType Directory -Force -Path $MatchDir | Out-Null

# 3. Download pre-built rules (no Python, no Git required)
Write-Host "Downloading Refuos rules..."
Write-Host ""

$ChecksumFile = Join-Path $env:TEMP "refuos-checksums.sha256"
try {
    # Download checksums file for integrity verification
    Invoke-WebRequest -Uri "$BaseUrl/checksums.sha256" -OutFile $ChecksumFile -UseBasicParsing
    $ChecksumLines = Get-Content $ChecksumFile

    foreach ($pkg in $Packages) {
        $url = "$BaseUrl/$pkg"
        $dest = Join-Path $MatchDir $pkg
        Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing

        # Verify integrity using SHA256
        $actual = (Get-FileHash -Path $dest -Algorithm SHA256).Hash.ToLower()
        $expected = ($ChecksumLines | Where-Object { $_ -match $pkg } | ForEach-Object { ($_ -split '\s+')[0] } | Select-Object -First 1)
        if ($actual -ne $expected) {
            Write-Host "Error: checksum mismatch for $pkg (expected $expected, got $actual)"
            Remove-Item -Force $dest -ErrorAction SilentlyContinue
            exit 1
        }
        Write-Host "  ok  $pkg"
    }
} finally {
    Remove-Item -Force $ChecksumFile -ErrorAction SilentlyContinue
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
