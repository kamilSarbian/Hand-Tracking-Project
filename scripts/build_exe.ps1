param(
    [ValidateSet("onedir", "onefile", "all")]
    [string]$Mode = "all"
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pythonPath = Join-Path $projectRoot ".venv-build\Scripts\python.exe"
$specPath = Join-Path $projectRoot "hand_tracking.spec"
$modelPath = Join-Path $projectRoot "models_assets\hand_landmarker.task"
$settingsPath = Join-Path $projectRoot "settings.json"

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Virtual environment interpreter not found: $pythonPath"
}
if (-not (Test-Path -LiteralPath $modelPath -PathType Leaf)) {
    throw "MediaPipe model not found: $modelPath"
}
if (-not (Test-Path -LiteralPath $settingsPath -PathType Leaf)) {
    throw "Application settings not found: $settingsPath"
}

$buildModes = if ($Mode -eq "all") { @("onedir", "onefile") } else { @($Mode) }
$previousBuildMode = [Environment]::GetEnvironmentVariable(
    "HAND_TRACKING_BUILD_MODE",
    "Process"
)
$previousDataDirectory = [Environment]::GetEnvironmentVariable(
    "GESTURE_DRAWING_APP_DATA_DIR",
    "Process"
)

Push-Location $projectRoot
try {
    foreach ($buildMode in $buildModes) {
        $env:HAND_TRACKING_BUILD_MODE = $buildMode
        $distPath = Join-Path $projectRoot "dist\$buildMode"
        $workPath = Join-Path $projectRoot "build\$buildMode"

        & $pythonPath -m PyInstaller `
            --noconfirm `
            --clean `
            --distpath $distPath `
            --workpath $workPath `
            $specPath

        if ($LASTEXITCODE -ne 0) {
            throw "PyInstaller failed for build mode: $buildMode"
        }

        $executablePath = if ($buildMode -eq "onefile") {
            Join-Path $distPath "GestureDrawingApp.exe"
        }
        else {
            Join-Path $distPath "GestureDrawingApp-debug\GestureDrawingApp-debug.exe"
        }
        if (-not (Test-Path -LiteralPath $executablePath -PathType Leaf)) {
            throw "Built executable not found: $executablePath"
        }

        $env:GESTURE_DRAWING_APP_DATA_DIR = Join-Path $workPath "self-test-data"
        $selfCheckProcess = Start-Process `
            -FilePath $executablePath `
            -ArgumentList "--self-test" `
            -WindowStyle Hidden `
            -Wait `
            -PassThru
        if ($selfCheckProcess.ExitCode -ne 0) {
            throw "Executable self-check failed for build mode: $buildMode"
        }
    }
}
finally {
    [Environment]::SetEnvironmentVariable(
        "HAND_TRACKING_BUILD_MODE",
        $previousBuildMode,
        "Process"
    )
    [Environment]::SetEnvironmentVariable(
        "GESTURE_DRAWING_APP_DATA_DIR",
        $previousDataDirectory,
        "Process"
    )
    Pop-Location
}
