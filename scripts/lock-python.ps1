# Régénérer les verrous uniquement lors d'une mise à jour volontaire des dépendances.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path -LiteralPath '.env')) {
    & (Join-Path $PSScriptRoot 'setup.ps1') -EnvironmentOnly
}
docker compose --profile tools run --rm lock
if ($LASTEXITCODE -ne 0) {
    throw 'Résolution Python interrompue. Vérifiez le réseau puis relancez ; le cache Docker est conservé.'
}
Write-Host 'Verrous générés sous Python 3.12. Examinez les fichiers requirements*.txt puis versionnez-les.'
