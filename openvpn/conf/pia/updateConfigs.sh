#!/bin/bash

set -e

# If the script is called from elsewhere
cd "${0%/*}"

# Delete everything (not this script though)
find . ! -name '*.sh' -delete

# Get updated configuration zip
curl -kL https://www.privateinternetaccess.com/openvpn/openvpn.zip -o openvpn.zip \
  && unzip -j openvpn.zip && rm openvpn.zip

# Ensure linux line endings
dos2unix *

case $(uname) in
  Darwin)
    SED=gsed
    ;;
  *)
    SED=sed
    ;;
esac

# Update configs with correct paths
$SED -i "s/ca ca\.rsa\.2048\.crt/ca \/etc\/openvpn\/conf\/pia\/ca\.rsa\.2048\.crt/" *.ovpn
$SED -i "s/crl-verify crl\.rsa\.2048\.pem/crl-verify \/etc\/openvpn\/conf\/pia\/crl\.rsa\.2048\.pem/" *.ovpn
$SED -i "s/auth-user-pass/auth-user-pass \/config\/openvpn-credentials.txt/" *.ovpn

# Create symlink for default.ovpn
ln -s Netherlands.ovpn default.ovpn
