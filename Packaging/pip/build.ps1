$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ../..

$py = (Get-Command py -ErrorAction SilentlyContinue)
if ($py) {
  py -m pip install --upgrade pip
  py -m pip install --upgrade build
  py -m build Packaging/pip --outdir Packaging/pip/dist
} else {
  python -m pip install --upgrade pip
  python -m pip install --upgrade build
  python -m build Packaging/pip --outdir Packaging/pip/dist
}

Write-Host "Built Packaging/pip/dist/"

