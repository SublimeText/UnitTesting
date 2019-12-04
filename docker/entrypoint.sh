#!/bin/bash

echo PACKAGE = $PACKAGE

set -e

PATH="$HOME/.local/bin:$PATH"
sudo sh -e /etc/init.d/xvfb start
/docker.sh bootstrap
/docker.sh install_package_control
/docker.sh run_tests --coverage
