#!/bin/sh
set -e

uv venv -p 3.12 .venv
uv pip install -U syft-core httpx
. .venv/bin/activate

while true; do
    echo "Running 'broadcast' with $(python3 --version) at '$(which python3)'"
    uv run python3 main.py

    echo "Sleeping for 10 seconds..."
    sleep 10
done

deactivate
