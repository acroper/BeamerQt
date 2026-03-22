#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

dist_path="Packaging/Linux/dist"
work_path="Packaging/Linux/build"
spec_path="Packaging/Linux"
spec_file="Packaging/common/BeamerQt.spec"

python3 -m pip install --upgrade pip
python3 -m pip install -r Packaging/requirements.txt -r Packaging/requirements-build.txt

pyinstaller "$spec_file" --noconfirm --clean --distpath "$dist_path" --workpath "$work_path" --specpath "$spec_path"

echo "Built $dist_path/BeamerQt/"

