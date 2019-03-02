#!/usr/bin/env bash

if [ -d venvProcurement ]; then
    source venvProcurement/bin/activate
fi

cd src/python
python3 utdesign_procurement
