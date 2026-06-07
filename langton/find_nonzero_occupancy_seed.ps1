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
    $processInfo.Arguments = "main.py -s $seed -i 250"
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

            $reportMessage = "Reejecutando con --report y --csv para generar el informe y las estadísticas..."
            Write-Host $reportMessage -ForegroundColor Cyan
            Write-Log $reportMessage $logFile

            $reportProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
            $reportProcessInfo.FileName = 'python'
            $reportProcessInfo.Arguments = "main.py -s $seed -i 250 --report --csv"
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

            $csvPath = $null
            foreach ($line in ($reportStdout -split "`r?`n")) {
                if ($line -match 'Statistics exported:\s*(.+\.csv)') {
                    $csvPath = $matches[1].Trim()
                    break
                }
            }

            if (-not $csvPath) {
                $csvDir = Join-Path $scriptDir 'output'
                $csvFile = Get-ChildItem -Path $csvDir -Filter '*.csv' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
                if ($csvFile) {
                    $csvPath = $csvFile.FullName
                }
            }

            $entry80 = $null
            $entry80Found = $false
            foreach ($line in ($reportStdout -split "`r?`n")) {
                if ($line -match 'Iteración 80:\s*([0-9]+)\s*hormigas') {
                    $entry80 = [int]$matches[1]
                    $entry80Found = $true
                    break
                }
            }

            if (-not $entry80Found -and $csvPath -and (Test-Path $csvPath)) {
                $entry80Row = Import-Csv -Path $csvPath | Where-Object { [int]$_.generation -eq 80 } | Select-Object -First 1
                if ($entry80Row) {
                    $entry80 = [int]$entry80Row.total_ants
                    $entry80Found = $true
                }
            }

            if ($entry80Found) {
                $entryMessage = "Iteración 80: $entry80 hormigas"
                Write-Host $entryMessage -ForegroundColor Yellow
                Write-Log $entryMessage $logFile
            } elseif ($csvPath -and (Test-Path $csvPath)) {
                $missingMessage = "No se encontró la generación 80 en el CSV: $csvPath"
                Write-Host $missingMessage -ForegroundColor Yellow
                Write-Log $missingMessage $logFile
            } else {
                $missingMessage = "No se pudo localizar el archivo CSV para extraer la generación 80."
                Write-Host $missingMessage -ForegroundColor Yellow
                Write-Log $missingMessage $logFile
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