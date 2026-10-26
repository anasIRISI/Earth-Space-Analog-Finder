$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Échec de $Executable $($Arguments -join ' ')" }
}
Invoke-Checked 'docker' @('compose', 'up', '-d', '--wait', 'db')
Invoke-Checked 'docker' @('compose', 'run', '--rm', 'backend', 'python', 'manage.py', 'check')
Invoke-Checked 'docker' @('compose', 'run', '--rm', 'backend', 'python', 'manage.py', 'test', '--noinput')
Invoke-Checked 'docker' @('compose', 'run', '--rm', 'backend', 'python', 'manage.py', 'spectacular', '--validate', '--fail-on-warn', '--file', '/tmp/schema.yaml')
Push-Location -LiteralPath 'frontend'
try {
    Invoke-Checked 'npm.cmd' @('run', 'test')
    Invoke-Checked 'npm.cmd' @('run', 'build')
} finally { Pop-Location }
