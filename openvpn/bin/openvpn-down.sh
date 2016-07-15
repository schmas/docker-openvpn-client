#!/bin/sh

echo "Running OpenVPN DOWN scripts."
/usr/local/bin/run-files-from-dir "/etc/openvpn/down" $@