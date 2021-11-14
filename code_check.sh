#!/bin/sh

pip install black isort mypy

mypy .
isort . --check
black . --check
