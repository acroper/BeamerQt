#!/usr/bin/env bash

cd "$(dirname "$0")"

if [ -d "pythonenv" ]; then
    source pythonenv/bin/activate
fi

python3 main.py
