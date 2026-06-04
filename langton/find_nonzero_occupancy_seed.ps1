# Prueba semillas aleatorias para `python main.py -s <seed>`
# y se detiene cuando la salida contiene un valor de ocupación final distinto de 0.00%.

Set-Strictmode -Version Latest

# Usamos $PSScriptRoot que es más limpio y directo
$scriptDir = $PSScriptRoot
Set-Location $scriptDir

$logDir = Join-Path $scriptDir 'output\logs'
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

function Get-RandomSeed {
    return Get-Random -Minimum 1 -Maximum 1000000000
}

function Write-Log {
    param (
        [string]$Text,
        [string]$Path
    )
    Add-Content -Path $Path -Value $Text
}

$sessionTimestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logFile = Join-Path $logDir "find_seed_$sessionTimestamp.txt"
"Starting seed search session at $(Get-Date -Format 'u')" | Out-File -FilePath $logFile -Encoding utf8

while ($true) {
    $seed = Get-RandomSeed
    Write-Host "Probando seed: $seed" -ForegroundColor Cyan

    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = 'python'
    $processInfo.Arguments = "main.py -s $seed"
    $processInfo.WorkingDirectory = $scriptDir # ◄--- FIJA EL DIRECTORIO DE TRABAJO AQUÍ
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    $processInfo.UseShellExecute = $false
    $processInfo.CreateNoWindow = $true

    $process = [System.Diagnostics.Process]::Start($processInfo)
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    if ($stdout) {
        Write-Host $stdout
        Write-Log $stdout $logFile
    }
    if ($stderr) {
        Write-Host "ERROR:" -ForegroundColor Red
        Write-Host $stderr
        Write-Log "ERROR: $stderr" $logFile
    }

    $match = [regex]::Match($stdout, 'Final occupancy:\s*([0-9]+\.[0-9]{2})%')
    if ($match.Success) {
        $occupancy = [decimal]$match.Groups[1].Value
        if ($occupancy -ne 0.00) {
            $foundMessage = "`n➡ Seed encontrada: $seed"
            Write-Host $foundMessage -ForegroundColor Green
            Write-Host "➡ Final occupancy: $occupancy%" -ForegroundColor Green
            Write-Log $foundMessage $logFile
            Write-Log "➡ Final occupancy: $occupancy%" $logFile

            $reportMessage = "Reejecutando con --report para generar el informe..."
            Write-Host $reportMessage -ForegroundColor Cyan
            Write-Log $reportMessage $logFile

            $reportProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
            $reportProcessInfo.FileName = 'python'
            $reportProcessInfo.Arguments = "main.py -s $seed --report"
            $reportProcessInfo.WorkingDirectory = $scriptDir # ◄--- Y AQUÍ TAMBIÉN
            $reportProcessInfo.RedirectStandardOutput = $true
            $reportProcessInfo.RedirectStandardError = $true
            $reportProcessInfo.UseShellExecute = $false
            $reportProcessInfo.CreateNoWindow = $true

            $reportProcess = [System.Diagnostics.Process]::Start($reportProcessInfo)
            $reportStdout = $reportProcess.StandardOutput.ReadToEnd()
            $reportStderr = $reportProcess.StandardError.ReadToEnd()
            $reportProcess.WaitForExit()

            if ($reportStdout) {
                Write-Host $reportStdout
                Write-Log $reportStdout $logFile
            }
            if ($reportStderr) {
                Write-Host "ERROR en reporte:" -ForegroundColor Red
                Write-Host $reportStderr
                Write-Log "ERROR en reporte: $reportStderr" $logFile
            }

            break
        }
    } else {
        Write-Host "No se encontró la línea 'Final occupancy:' en la salida." -ForegroundColor Yellow
    }

    Start-Sleep -Seconds 1
}

$endMessage = "Script terminado. Log guardado en: $logFile"
Write-Host $endMessage -ForegroundColor White
Write-Log $endMessage $logFile