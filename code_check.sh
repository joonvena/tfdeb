#!/bin/sh
set -e

pip install -r requirements.txt
pip install black isort pyre-check

pyre check
isort . --check
black . --check
