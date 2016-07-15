#!/bin/sh

if [ $1 -ne 0 ]; then
    echo "Error starting OPENVPN!"
    kill-all-processes
fi