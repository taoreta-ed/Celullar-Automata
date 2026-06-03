# Prueba semillas aleatorias para `python main.py -s <seed>`
# y se detiene cuando la salida contiene un valor de ocupación final distinto de 0.00%.

Set-Strictmode -Version Latest

# Usamos $PSScriptRoot que es más limpio y directo
$scriptDir = $PSScriptRoot
Set-Location $scriptDir

function Get-RandomSeed {
    return Get-Random -Minimum 1 -Maximum 1000000000
}

while ($true) {
    $seed = Get-RandomSeed
    Write-Host "Probando seed: $seed" -ForegroundColor Cyan

    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = 'python'
    $processInfo.Arguments = "main.py -s $seed -g 300"
    $processInfo.WorkingDirectory = $scriptDir # ◄--- FIJA EL DIRECTORIO DE TRABAJO AQUÍ
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    $processInfo.UseShellExecute = $false
    $processInfo.CreateNoWindow = $true

    $process = [System.Diagnostics.Process]::Start($processInfo)
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    Write-Host $stdout
    if ($stderr) {
        Write-Host "ERROR:" -ForegroundColor Red
        Write-Host $stderr
    }

    $match = [regex]::Match($stdout, 'Final occupancy:\s*([0-9]+\.[0-9]{2})%')
    if ($match.Success) {
        $occupancy = [decimal]$match.Groups[1].Value
        if ($occupancy -ne 0.00) {
            Write-Host "`n➡ Seed encontrada: $seed" -ForegroundColor Green
            Write-Host "➡ Final occupancy: $occupancy%" -ForegroundColor Green

            Write-Host "Reejecutando con --report para generar el informe..." -ForegroundColor Cyan
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

            Write-Host $reportStdout
            if ($reportStderr) {
                Write-Host "ERROR en reporte:" -ForegroundColor Red
                Write-Host $reportStderr
            }

            break
        }
    } else {
        Write-Host "No se encontró la línea 'Final occupancy:' en la salida." -ForegroundColor Yellow
    }

    Start-Sleep -Seconds 1
}

Write-Host "Script terminado." -ForegroundColor White