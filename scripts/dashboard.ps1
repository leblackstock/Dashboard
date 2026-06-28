param(
    [Parameter(Position = 0)]
    [ValidateSet("install-task", "uninstall-task", "start", "stop", "restart", "status")]
    [string]$Action = "status"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$StateDirectory = Join-Path $RepoRoot ".run"
$StatePath = Join-Path $StateDirectory "dashboard-processes.json"
$BackendUrl = "http://127.0.0.1:8000"
$FrontendUrl = "http://127.0.0.1:5173"
$ScheduledTaskName = "Dashboard Local Runtime"
$ScheduledTaskPath = "\"
$ScheduledTaskDescription = "Managed by Dashboard scripts/dashboard.ps1. Starts the local web app only."
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

function Get-DashboardScheduledTask {
    return Get-ScheduledTask `
        -TaskName $ScheduledTaskName `
        -TaskPath $ScheduledTaskPath `
        -ErrorAction SilentlyContinue
}

function Test-OwnedScheduledTask {
    param([object]$Task)
    return $null -ne $Task -and $Task.Description -eq $ScheduledTaskDescription
}

function Show-ScheduledTaskStatus {
    $task = Get-DashboardScheduledTask
    if ($null -eq $task) {
        Write-Host "Login task: not installed."
        return $true
    }
    if (-not (Test-OwnedScheduledTask -Task $task)) {
        Write-Host "Login task: name conflict; the existing task is not managed by Dashboard."
        return $false
    }
    Write-Host "Login task: installed ($($task.State))."
    return $true
}

function Install-DashboardScheduledTask {
    $existingTask = Get-DashboardScheduledTask
    if ($null -ne $existingTask -and -not (Test-OwnedScheduledTask -Task $existingTask)) {
        Write-Host "The dashboard task name is already used by an unrelated task. Nothing was changed."
        return $false
    }

    try {
        $scriptArguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$PSCommandPath`" start"
        $taskAction = New-ScheduledTaskAction `
            -Execute "powershell.exe" `
            -Argument $scriptArguments `
            -WorkingDirectory $RepoRoot
        $taskTrigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser
        $taskPrincipal = New-ScheduledTaskPrincipal `
            -UserId $CurrentUser `
            -LogonType Interactive `
            -RunLevel Limited
        $taskSettings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable `
            -MultipleInstances IgnoreNew `
            -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
        $taskDefinition = New-ScheduledTask `
            -Action $taskAction `
            -Trigger $taskTrigger `
            -Principal $taskPrincipal `
            -Settings $taskSettings `
            -Description $ScheduledTaskDescription

        Register-ScheduledTask `
            -TaskName $ScheduledTaskName `
            -TaskPath $ScheduledTaskPath `
            -InputObject $taskDefinition `
            -Force | Out-Null

        Start-ScheduledTask -TaskName $ScheduledTaskName -TaskPath $ScheduledTaskPath
        $backendReady = Wait-ForHttp -Uri "$BackendUrl/api/health"
        $dailyReady = Wait-ForHttp -Uri "$BackendUrl/api/daily"
        $frontendReady = Wait-ForHttp -Uri "$FrontendUrl/"

        Write-Host "Dashboard login task installed for the current user."
        Write-Host "Administrator privileges: not required."
        if ($backendReady -and $dailyReady -and $frontendReady) {
            Write-Host "Dashboard startup verification: OK"
            return $true
        }
        Write-Host "The login task was installed, but the dashboard did not become healthy. Check dashboard status."
        return $false
    }
    catch {
        Write-Host "Dashboard login task installation failed. No unrelated tasks were changed."
        return $false
    }
}

function Uninstall-DashboardScheduledTask {
    $task = Get-DashboardScheduledTask
    if ($null -eq $task) {
        Write-Host "Dashboard login task is already uninstalled."
        return $true
    }
    if (-not (Test-OwnedScheduledTask -Task $task)) {
        Write-Host "The matching task name is not managed by Dashboard and was not removed."
        return $false
    }

    try {
        Unregister-ScheduledTask `
            -TaskName $ScheduledTaskName `
            -TaskPath $ScheduledTaskPath `
            -Confirm:$false
        Write-Host "Dashboard login task uninstalled. Running dashboard processes were not changed."
        return $true
    }
    catch {
        Write-Host "Dashboard login task could not be uninstalled. No unrelated tasks were changed."
        return $false
    }
}

function Get-DashboardState {
    if (-not (Test-Path -LiteralPath $StatePath)) {
        return $null
    }
    try {
        return Get-Content -LiteralPath $StatePath -Raw -Encoding utf8 | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function Get-StateEntry {
    param(
        [object]$State,
        [string]$Name
    )
    if ($null -eq $State) {
        return $null
    }
    $property = $State.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }
    return $property.Value
}

function New-StateEntry {
    param([System.Diagnostics.Process]$Process)
    return [ordered]@{
        pid = $Process.Id
        process_name = $Process.ProcessName
        started_at = $Process.StartTime.ToUniversalTime().ToString("o")
    }
}

function Get-ValidatedProcess {
    param([object]$Entry)
    if ($null -eq $Entry) {
        return $null
    }
    try {
        $process = Get-Process -Id ([int]$Entry.pid) -ErrorAction Stop
        $expectedStart = [DateTime]::Parse([string]$Entry.started_at).ToUniversalTime()
        $actualStart = $process.StartTime.ToUniversalTime()
        if (
            $process.ProcessName -ne [string]$Entry.process_name -or
            $process.Id -ne [int]$Entry.pid -or
            $actualStart.Ticks -ne $expectedStart.Ticks
        ) {
            return $null
        }
        return $process
    }
    catch {
        return $null
    }
}

function Remove-DashboardState {
    if (Test-Path -LiteralPath $StatePath) {
        Remove-Item -LiteralPath $StatePath -Force
    }
}

function Test-PortOccupied {
    param([int]$Port)
    return @(
        Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    ).Count -gt 0
}

function Test-HttpOk {
    param([string]$Uri)
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Uri -TimeoutSec 2
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

function Wait-ForHttp {
    param(
        [string]$Uri,
        [int]$Attempts = 40
    )
    for ($attempt = 0; $attempt -lt $Attempts; $attempt += 1) {
        if (Test-HttpOk -Uri $Uri) {
            return $true
        }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

function Stop-OwnedProcess {
    param([object]$Entry)
    $process = Get-ValidatedProcess -Entry $Entry
    if ($null -eq $process) {
        return $false
    }

    $taskkill = Join-Path $env:SystemRoot "System32\taskkill.exe"
    & $taskkill /PID $process.Id /T /F *> $null
    return $true
}

function Show-DashboardStatus {
    $scheduledTaskHealthy = Show-ScheduledTaskStatus
    $state = Get-DashboardState
    if ($null -eq $state) {
        Write-Host "Dashboard status: stopped."
        return $scheduledTaskHealthy
    }

    $backend = Get-ValidatedProcess -Entry (Get-StateEntry -State $state -Name "backend")
    $frontend = Get-ValidatedProcess -Entry (Get-StateEntry -State $state -Name "frontend")
    $backendHealthy = $null -ne $backend -and (Test-HttpOk -Uri "$BackendUrl/api/health")
    $dailyHealthy = $null -ne $backend -and (Test-HttpOk -Uri "$BackendUrl/api/daily")
    $frontendHealthy = $null -ne $frontend -and (Test-HttpOk -Uri "$FrontendUrl/")

    Write-Host "Backend: $(if ($backendHealthy) { 'running' } else { 'stopped or unhealthy' })"
    Write-Host "Daily API: $(if ($dailyHealthy) { 'OK' } else { 'unavailable' })"
    Write-Host "Frontend: $(if ($frontendHealthy) { 'running' } else { 'stopped or unhealthy' })"
    if ($backendHealthy -and $dailyHealthy -and $frontendHealthy) {
        Write-Host "Dashboard URL: $FrontendUrl/"
        return $scheduledTaskHealthy
    }
    return $false
}

function Stop-Dashboard {
    param([switch]$Quiet)
    $state = Get-DashboardState
    if ($null -eq $state) {
        if (-not $Quiet) {
            Write-Host "Dashboard is already stopped."
        }
        return $true
    }

    $frontendStopped = Stop-OwnedProcess -Entry (Get-StateEntry -State $state -Name "frontend")
    $backendStopped = Stop-OwnedProcess -Entry (Get-StateEntry -State $state -Name "backend")
    Remove-DashboardState

    if (-not $Quiet) {
        if (-not $frontendStopped) {
            Write-Host "Frontend process was not validated and was not stopped."
        }
        if (-not $backendStopped) {
            Write-Host "Backend process was not validated and was not stopped."
        }
        Write-Host "Dashboard stop complete."
    }
    return $true
}

function Start-Dashboard {
    $existingState = Get-DashboardState
    if ($null -ne $existingState) {
        $backend = Get-ValidatedProcess -Entry (Get-StateEntry -State $existingState -Name "backend")
        $frontend = Get-ValidatedProcess -Entry (Get-StateEntry -State $existingState -Name "frontend")
        if ($null -ne $backend -and $null -ne $frontend) {
            Write-Host "Dashboard is already running."
            return Show-DashboardStatus
        }
        Stop-Dashboard -Quiet | Out-Null
    }

    $occupiedPorts = @(
        @(8000, 5173) | Where-Object { Test-PortOccupied -Port $_ }
    )
    if ($occupiedPorts.Count -gt 0) {
        Write-Host "Dashboard could not start because a required port is already in use. No processes were stopped."
        return $false
    }

    $uv = Get-Command uv -ErrorAction SilentlyContinue
    $npx = Get-Command npx.cmd -ErrorAction SilentlyContinue
    if ($null -eq $uv -or $null -eq $npx) {
        Write-Host "Dashboard prerequisites are missing. Install uv and Node.js/npm first."
        return $false
    }

    New-Item -ItemType Directory -Path $StateDirectory -Force | Out-Null
    $backendProcess = $null
    $frontendProcess = $null
    $startPhase = "backend launch"
    try {
        $backendStart = @{
            FilePath = $uv.Source
            ArgumentList = @(
                "run", "uvicorn", "backend.app.main:app",
                "--host", "127.0.0.1", "--port", "8000"
            )
            WorkingDirectory = $RepoRoot
            WindowStyle = "Hidden"
            PassThru = $true
        }
        $backendProcess = Start-Process @backendStart

        $startPhase = "frontend launch"
        $frontendStart = @{
            FilePath = $npx.Source
            ArgumentList = @(
                "pnpm@9.15.9", "dev", "--",
                "--host", "127.0.0.1", "--port", "5173"
            )
            WorkingDirectory = (Join-Path $RepoRoot "frontend")
            WindowStyle = "Hidden"
            PassThru = $true
        }
        $frontendProcess = Start-Process @frontendStart

        $startPhase = "process state validation"
        $state = [ordered]@{
            version = 1
            backend = New-StateEntry -Process $backendProcess
            frontend = New-StateEntry -Process $frontendProcess
        }
        $state | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $StatePath -Encoding utf8

        $startPhase = "health verification"
        $backendReady = Wait-ForHttp -Uri "$BackendUrl/api/health"
        $dailyReady = Wait-ForHttp -Uri "$BackendUrl/api/daily"
        $frontendReady = Wait-ForHttp -Uri "$FrontendUrl/"
        if (-not ($backendReady -and $dailyReady -and $frontendReady)) {
            throw "dashboard_start_failed"
        }

        Write-Host "Dashboard started."
        Write-Host "Backend health: OK"
        Write-Host "Daily API: OK"
        Write-Host "Frontend: OK"
        Write-Host "Dashboard URL: $FrontendUrl/"
        return $true
    }
    catch {
        foreach ($process in @($frontendProcess, $backendProcess)) {
            if ($null -ne $process) {
                Stop-OwnedProcess -Entry (New-StateEntry -Process $process) | Out-Null
            }
        }
        Remove-DashboardState
        Write-Host "Dashboard could not start during $startPhase. Started processes were stopped."
        return $false
    }
}

$succeeded = switch ($Action) {
    "install-task" { Install-DashboardScheduledTask }
    "uninstall-task" { Uninstall-DashboardScheduledTask }
    "start" { Start-Dashboard }
    "stop" { Stop-Dashboard }
    "restart" {
        Stop-Dashboard -Quiet | Out-Null
        Start-Dashboard
    }
    "status" { Show-DashboardStatus }
}

if (-not $succeeded) {
    exit 1
}
