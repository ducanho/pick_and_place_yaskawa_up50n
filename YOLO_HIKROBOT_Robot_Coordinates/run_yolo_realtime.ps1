$ErrorActionPreference = 'Stop'
$pythonCandidates = @()
$environmentRoots = @($PSScriptRoot, (Split-Path -Parent $PSScriptRoot))
foreach ($environmentRoot in $environmentRoots) {
    $localPython = Join-Path $environmentRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $localPython) {
        $pythonCandidates += $localPython
        $basePython = & $localPython -c 'import sys; print(sys._base_executable)'
        if ($LASTEXITCODE -eq 0) { $pythonCandidates += $basePython }
    }
}
$pythonCandidates += @(Get-Command python -CommandType Application -All -ErrorAction SilentlyContinue | ForEach-Object { $_.Source })
$probe = 'import cv2, ultralytics; assert any(s.strip().startswith("GUI:") and s.split(":", 1)[1].strip() != "NONE" for s in cv2.getBuildInformation().splitlines())'
foreach ($pythonPath in ($pythonCandidates | Select-Object -Unique)) {
    if (-not (Test-Path -LiteralPath $pythonPath)) { continue }
    # Feed code through stdin so Windows native argument quoting cannot alter it.
    $ErrorActionPreference = 'Continue'
    $probe | & $pythonPath - 2>$null | Out-Null
    $probeExit = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($probeExit -eq 0) {
        & $pythonPath (Join-Path $PSScriptRoot 'yolo_camera_robot_realtime.py') @args
        exit $LASTEXITCODE
    }
}
Write-Host 'No Python environment with ultralytics and OpenCV GUI was found.'
Write-Host 'Install requirements-realtime.txt in the intended Python environment.'
exit 1
