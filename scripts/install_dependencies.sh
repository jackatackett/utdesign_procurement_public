#!/usr/bin/env bash

if [ -d venvProcurement ]; then
    source venvProcurement/bin/activate
fi

python3 -m pip install -r requirements.txt
