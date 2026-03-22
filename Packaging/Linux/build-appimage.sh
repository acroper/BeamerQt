#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

# 1) Build the PyInstaller bundle (into Packaging/Linux/dist)
./Packaging/Linux/build.sh

appdir_root="Packaging/Linux/build/AppImage"
appdir="$appdir_root/BeamerQt.AppDir"
dist_dir="Packaging/Linux/dist"
bundle_dir="$dist_dir/BeamerQt"

rm -rf "$appdir_root"
mkdir -p "$appdir/usr/bin"

if [[ ! -d "$bundle_dir" ]]; then
  echo "Missing PyInstaller output: $bundle_dir" >&2
  exit 1
fi

# 2) Stage AppDir (PyInstaller already contains the needed libs)
cp -R "$bundle_dir/"* "$appdir/usr/bin/"

cat > "$appdir/AppRun" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec "$HERE/usr/bin/BeamerQt" "$@"
EOF
chmod +x "$appdir/AppRun"

cat > "$appdir/BeamerQt.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=BeamerQt
Exec=BeamerQt
Icon=beamerqt
Categories=Office;Education;
Terminal=false
EOF

# AppImage tooling commonly picks up the icon from the AppDir root.
cp -f "gui/icons/BQTIcon.png" "$appdir/beamerqt.png"

# 3) Build AppImage
# Provide appimagetool either in PATH or via APPIMAGETOOL env var.
appimagetool="${APPIMAGETOOL:-}"
if [[ -z "$appimagetool" ]]; then
  if command -v appimagetool >/dev/null 2>&1; then
    appimagetool="appimagetool"
  elif [[ -x "Packaging/Linux/tools/appimagetool.AppImage" ]]; then
    appimagetool="Packaging/Linux/tools/appimagetool.AppImage"
  fi
fi

if [[ -z "$appimagetool" ]]; then
  echo "appimagetool not found." >&2
  echo "Install it, or set APPIMAGETOOL=/path/to/appimagetool, or put Packaging/Linux/tools/appimagetool.AppImage." >&2
  exit 2
fi

version="${VERSION:-dev}"
arch="$(uname -m)"
out="$dist_dir/BeamerQt-${version}-${arch}.AppImage"

"$appimagetool" "$appdir" "$out"
chmod +x "$out" || true

echo "Built $out"

