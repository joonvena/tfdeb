#!/bin/sh

pip install black isort

isort .
black . --check
