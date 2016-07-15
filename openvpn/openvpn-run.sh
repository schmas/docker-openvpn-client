#!/bin/sh
exec 2>&1

echo "OpenVPN OPTS: ${OPENVPN_OPTS}"
echo "OpenVPN config: ${OPENVPN_CONFIG}"
exec openvpn --script-security 2 --up "/usr/local/bin/ssh-restart" $OPENVPN_OPTS --config "$OPENVPN_CONFIG"