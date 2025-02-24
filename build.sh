#!/bin/sh
cd `dirname $0`

. venv/bin/activate

pyinstaller --onefile --hidden-import="googleapiclient" src/main.py
tar -czvf dist/archive.tar.gz ./dist/main
