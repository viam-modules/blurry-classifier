#!/bin/sh
cd `dirname $0`

. venv/bin/activate

python -m PyInstaller --onefile --hidden-import="googleapiclient" src/main.py
tar -czvf dist/archive.tar.gz ./dist/main
