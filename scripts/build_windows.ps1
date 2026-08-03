$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$modelSource = Join-Path $projectRoot "models\yolo26n-pose.pt"
$distributionRoot = Join-Path $projectRoot "dist\WorkoutPoseChecker"
$modelDestination = Join-Path $distributionRoot "models"

if (-not (Test-Path -LiteralPath $modelSource)) {
    throw "모델 파일을 찾을 수 없습니다: $modelSource"
}

Push-Location $projectRoot
try {
    python -m PyInstaller --noconfirm --clean WorkoutPoseChecker.spec

    New-Item -ItemType Directory -Force -Path $modelDestination | Out-Null
    Copy-Item -LiteralPath $modelSource -Destination $modelDestination -Force
}
finally {
    Pop-Location
}

Write-Output "빌드 완료: $distributionRoot"
