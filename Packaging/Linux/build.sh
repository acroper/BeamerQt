#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

dist_path="Packaging/Linux/dist"
work_path="Packaging/Linux/build"
spec_file="Packaging/common/BeamerQt.spec"
venv_dir="${VENV_DIR:-pythonenv}"
python_bin="${PYTHON_BIN:-python3}"
install_deps="${INSTALL_DEPS:-auto}"

if [[ ! -d "$venv_dir" ]]; then
  "$python_bin" -m venv "$venv_dir"
fi

source "$venv_dir/bin/activate"

if [[ "$install_deps" == "always" ]] || [[ "$install_deps" == "auto" && ! -x "$venv_dir/bin/pyinstaller" ]]; then
  python3 -m pip install --upgrade pip
  python3 -m pip install -r Packaging/requirements.txt -r Packaging/requirements-build.txt
fi

pyinstaller "$spec_file" --noconfirm --clean --distpath "$dist_path" --workpath "$work_path"

echo "Built $dist_path/BeamerQt/"
