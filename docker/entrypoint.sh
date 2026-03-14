#!/bin/bash

echo PACKAGE = $PACKAGE

set -e

PATH="$HOME/.local/bin:$PATH"
BOOTSTRAP_MARKER="$HOME/.cache/unittesting/bootstrap.done"

sudo sh -e /etc/init.d/xvfb start

UNITTESTING_SOURCE=${UNITTESTING_SOURCE:-/unittesting}
if [ -d "$UNITTESTING_SOURCE/sbin" ]; then
    # Ensure UnitTesting comes from the local checkout running this script,
    # so first runs do not depend on tagged upstream releases.
    (cd "$UNITTESTING_SOURCE" && PACKAGE=UnitTesting /docker.sh copy_tested_package overwrite)
fi

if [ ! -f "$BOOTSTRAP_MARKER" ]; then
    # Bootstrap from a neutral cwd to avoid Windows worktree .git indirection
    # paths breaking git commands inside the Linux container.
    (cd /tmp && /docker.sh bootstrap skip_package_copy)
    /docker.sh install_package_control
    mkdir -p "$(dirname "$BOOTSTRAP_MARKER")"
    touch "$BOOTSTRAP_MARKER"
fi

# Always refresh checked-out package into Packages/<PACKAGE>
/docker.sh copy_tested_package overwrite

if [ "$#" -gt 0 ]; then
    /docker.sh "$@"
else
    /docker.sh run_tests --coverage
fi
