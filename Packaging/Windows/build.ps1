Param(
  [switch]$Clean
)

$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ../..

$distPath = "Packaging/Windows/dist"
$workPath = "Packaging/Windows/build"
$specPath = "Packaging/Windows"
$specFile = "Packaging/common/BeamerQt.spec"

if ($Clean) {
  if (Test-Path $workPath) { Remove-Item -Recurse -Force $workPath }
  if (Test-Path $distPath) { Remove-Item -Recurse -Force $distPath }
}

$py = (Get-Command py -ErrorAction SilentlyContinue)
if ($py) {
  py -m pip install --upgrade pip
  py -m pip install -r Packaging/requirements.txt -r Packaging/requirements-build.txt
} else {
  python -m pip install --upgrade pip
  python -m pip install -r Packaging/requirements.txt -r Packaging/requirements-build.txt
}

pyinstaller $specFile --noconfirm --clean --distpath $distPath --workpath $workPath --specpath $specPath

Write-Host "Built $distPath/BeamerQt/BeamerQt.exe"

