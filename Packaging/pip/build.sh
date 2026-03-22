#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build

python3 -m build Packaging/pip --outdir Packaging/pip/dist

echo "Built Packaging/pip/dist/"

