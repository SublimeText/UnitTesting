#! /usr/bin/env bash

set -e

echo "block sublime text ip address"
if [ $(uname) = 'Darwin' ]; then
    sudo route -n add -host 45.55.41.223 127.0.0.1
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    sudo apt-get install -y net-tools
    sudo route add -host 45.55.41.223 reject || echo "See https://github.com/SublimeText/UnitTesting/issues/190#issuecomment-850133753"
else
    pwsh -command 'New-NetFirewallRule -DisplayName "Block sublimetext.com IP address" -Direction Outbound -LocalPort Any -Protocol TCP -Action Block -RemoteAddress "45.55.41.223"'
fi
