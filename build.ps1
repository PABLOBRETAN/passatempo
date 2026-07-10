[CmdletBinding()]
param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSCommandPath
$player = Join-Path $projectRoot "flashplayer_32_sa.exe"
$games = Join-Path $projectRoot "JOGOS"

foreach ($requiredPath in @($player, $games)) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Arquivo ou pasta obrigatória não encontrada: $requiredPath"
    }
}

# Evita gerar uma release sem interface caso o Python escolhido esteja sem Tcl/Tk.
& $Python -c "import tkinter as tk; root = tk.Tk(); root.withdraw(); root.update_idletasks(); root.destroy()"
if ($LASTEXITCODE -ne 0) {
    throw "O Python informado não conseguiu iniciar o Tkinter. Instale ou use um Python com Tcl/Tk antes de gerar a release."
}

$releaseRoot = Join-Path $projectRoot "release"
$workPath = Join-Path $projectRoot "build\release"
$specPath = Join-Path $projectRoot "build\spec"
$source = Join-Path $projectRoot "play.py"

New-Item -ItemType Directory -Force -Path $releaseRoot, $workPath, $specPath | Out-Null

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onedir `
    --name "PlayOuro" `
    --distpath $releaseRoot `
    --workpath $workPath `
    --specpath $specPath `
    $source

if ($LASTEXITCODE -ne 0) {
    throw "O PyInstaller terminou com código $LASTEXITCODE."
}

$package = Join-Path $releaseRoot "PlayOuro"
$packageGames = Join-Path $package "JOGOS"

# O PyInstaller recria a pasta do aplicativo; removemos somente uma cópia antiga
# da biblioteca dentro da release para evitar jogos obsoletos no próximo pacote.
if (Test-Path -LiteralPath $packageGames) {
    Remove-Item -LiteralPath $packageGames -Recurse -Force
}

Copy-Item -LiteralPath $player -Destination (Join-Path $package "flashplayer_32_sa.exe") -Force
Copy-Item -LiteralPath $games -Destination $packageGames -Recurse -Force

Write-Host "Release pronta em: $package"
Write-Host "Abra PlayOuro.exe mantendo o Flash Player e a pasta JOGOS ao lado dele."
