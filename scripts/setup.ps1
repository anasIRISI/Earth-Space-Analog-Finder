[CmdletBinding()]
param([switch]$SkipFrontend, [switch]$EnvironmentOnly)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Échec de $Executable $($Arguments -join ' ')" }
}

if (-not (Test-Path -LiteralPath '.env')) {
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $secretBytes = New-Object byte[] 48
        $passwordBytes = New-Object byte[] 24
        $rng.GetBytes($secretBytes)
        $rng.GetBytes($passwordBytes)
        $secret = [Convert]::ToBase64String($secretBytes)
        $password = [Convert]::ToBase64String($passwordBytes)
        $content = [IO.File]::ReadAllText((Join-Path $projectRoot '.env.example'))
        $content = $content.Replace('replace-with-a-random-local-secret', $secret)
        $content = $content.Replace('replace-with-a-random-local-password', $password)
        [IO.File]::WriteAllText((Join-Path $projectRoot '.env'), $content, [Text.UTF8Encoding]::new($false))
        Write-Host '.env créé avec des secrets de développement aléatoires.'
    } finally { $rng.Dispose() }
} else { Write-Host '.env existant conservé.' }

if ($EnvironmentOnly) { return }

Invoke-Checked 'docker' @('info', '--format', '{{.ServerVersion}}')
Invoke-Checked 'docker' @('compose', 'config', '--quiet')
if (-not (Test-Path -LiteralPath 'backend/requirements.txt') -or -not (Test-Path -LiteralPath 'backend/requirements-dev.txt')) {
    Write-Host 'Génération des verrous Python 3.12. Le cache des téléchargements est conservé dans Docker.'
    Invoke-Checked 'docker' @('compose', '--profile', 'tools', 'run', '--rm', 'lock')
}
Invoke-Checked 'docker' @('compose', 'build', 'backend')
Invoke-Checked 'docker' @('compose', 'up', '-d', '--wait', 'db')
Invoke-Checked 'docker' @('compose', 'run', '--rm', 'backend', 'python', 'manage.py', 'migrate', '--noinput')
Invoke-Checked 'docker' @('compose', 'run', '--rm', 'backend', 'python', 'manage.py', 'check')
if (-not $SkipFrontend) {
    $nodeMajor = [int]((& node --version).TrimStart('v').Split('.')[0])
    if ($nodeMajor -ne 24) { throw 'Installez Node.js 24 LTS avant de continuer.' }
    Push-Location -LiteralPath (Join-Path $projectRoot 'frontend')
    try { Invoke-Checked 'npm.cmd' @('ci') } finally { Pop-Location }
}
Write-Host 'Initialisation terminée. Lancez docker compose up -d --wait backend puis npm run dev dans frontend.'
