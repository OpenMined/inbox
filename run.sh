#!/bin/sh
set -e

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    uv venv .venv
    echo "Virtual environment created successfully."
else
    echo "Virtual environment already exists."
fi

uv pip install -U syftbox

. .venv/bin/activate

echo "Running 'inbox' with $(python3 --version) at '$(which python3)'"
uv run python3 main.py

deactivate
