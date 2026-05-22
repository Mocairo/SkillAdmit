#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
