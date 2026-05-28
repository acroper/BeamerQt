#!/usr/bin/env bash

# Resolve script directory to execute relative to it
cd "$(dirname "$0")"

if [ ! -d "pythonenv" ]; then
    read -p "Folder 'pythonenv' does not exist. Do you want to create it? (y/N): " response
    if [[ "$response" =~ ^[yY](es)?$ ]]; then
        echo "Creating virtual environment 'pythonenv'..."
        python3 -m venv pythonenv
        if [ $? -eq 0 ]; then
            echo "Virtual environment 'pythonenv' created."
            echo "Installing pyqt6 and pymupdf..."
            ./pythonenv/bin/pip install --upgrade pip
            ./pythonenv/bin/pip install pyqt6 pymupdf
        else
            echo "Error: Failed to create virtual environment 'pythonenv'."
        fi
    else
        echo "Virtual environment creation skipped."
    fi
else
    echo "Folder 'pythonenv' already exists."
fi

echo ""
echo "--------------------------------------------------------"
echo "Recommendation:"
echo "It is highly recommended to install the following packages"
echo "on your system for full functionality:"
echo " - texlive-beamer (LaTeX Beamer class)"
echo " - inkscape (vector graphics editor)"
echo "--------------------------------------------------------"
