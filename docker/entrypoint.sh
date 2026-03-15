#!/bin/bash

echo PACKAGE = $PACKAGE

set -e

PATH="$HOME/.local/bin:$PATH"
BOOTSTRAP_MARKER="$HOME/.cache/unittesting/bootstrap.done"

ensure_git_identity() {
    # Align local container behavior with typical CI runners where git
    # identity is configured for tests that create commits.
    if ! git config --global user.name >/dev/null 2>&1; then
        git config --global user.name "${UNITTESTING_GIT_USER_NAME:-UnitTesting CI}"
    fi

    if ! git config --global user.email >/dev/null 2>&1; then
        git config --global user.email "${UNITTESTING_GIT_USER_EMAIL:-unittesting@example.invalid}"
    fi
}

sudo sh -e /etc/init.d/xvfb start
ensure_git_identity

UNITTESTING_SOURCE=${UNITTESTING_SOURCE:-/unittesting}
SUBLIME_TEXT_VERSION=${SUBLIME_TEXT_VERSION:-4}
if [ "$SUBLIME_TEXT_VERSION" -ge 4 ]; then
    ST_PACKAGES_DIR="$HOME/.config/sublime-text/Packages"
else
    ST_PACKAGES_DIR="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
fi

if [ -d "$UNITTESTING_SOURCE/sbin" ]; then
    # Ensure UnitTesting comes from the local checkout running this script,
    # so first runs do not depend on tagged upstream releases.
    (cd "$UNITTESTING_SOURCE" && PACKAGE=UnitTesting /docker.sh copy_tested_package overwrite)

    # Normalize CRLF in shell scripts copied from Windows workspaces.
    if [ -d "$ST_PACKAGES_DIR/UnitTesting/sbin" ]; then
        find "$ST_PACKAGES_DIR/UnitTesting/sbin" -type f -name "*.sh" -exec sed -i 's/\r$//' {} +
    fi
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
