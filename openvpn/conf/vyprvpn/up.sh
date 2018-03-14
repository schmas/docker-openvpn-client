#!/bin/sh
# Exit on error
set -e
# Back up the existing resolv conf
cat /etc/resolv.conf > /etc/resolv.conf.bak
# Configure the resolv conf from push settings
echo "nameserver $route_vpn_gateway" > /etc/resolv.conf
