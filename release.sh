#!/bin/bash
# release current branch to pypi

rm -r dist
python3 setup.py sdist
twine upload dist/*
