#!/bin/sh
set -e

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    uv venv .venv
    echo "Virtual environment created successfully."
    uv pip install -U syftbox
else
    echo "Virtual environment already exists."
fi

. .venv/bin/activate
uv run python3 main.py

deactivate
