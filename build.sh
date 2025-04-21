#!/bin/sh
cd `dirname $0`

. venv/bin/activate

python -m PyInstaller --onefile --hidden-import="googleapiclient" src/main.py
tar -czvf dist/archive.tar.gz ./dist/main
# To run locally, we need meta.json in the same directory. So, add to dist/ a
# symlink that goes one directory up to meta.json
ln -s -f ../meta.json dist
