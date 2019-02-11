#!/usr/bin/env bash

if [ -d venvProcurement ]; then
    source venvProcurement/bin/activate
fi

cd src/python/utdesign_procurement
python3 server.py