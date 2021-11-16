#!/bin/sh
set -e

pip install -r requirements.txt
pip install black isort mypy

mypy . --strict
isort . --check
black . --check
