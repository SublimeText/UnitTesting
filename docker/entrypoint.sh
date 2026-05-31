#!/bin/bash

echo PACKAGE = $PACKAGE

set -e

PATH="$HOME/.local/bin:$PATH"
BOOTSTRAP_MARKER="$HOME/.cache/unittesting/bootstrap.done"
DEPENDENCY_MARKER_DIR="$HOME/.cache/unittesting/package-dependencies"

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

ensure_ci_platform_compat() {
    # Some test suites key off Travis-style OS markers while others expect
    # GitHub Actions' RUNNER_OS naming.
    local travis_name=""
    local runner_name=""

    case "$(uname -s)" in
        Linux*)
            travis_name="linux"
            runner_name="Linux"
            ;;
        Darwin*)
            travis_name="osx"
            runner_name="macOS"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            travis_name="windows"
            runner_name="Windows"
            ;;
    esac

    if [ -n "$travis_name" ] && [ -z "$TRAVIS_OS_NAME" ]; then
        export TRAVIS_OS_NAME="$travis_name"
    fi

    if [ -n "$runner_name" ] && [ -z "$RUNNER_OS" ]; then
        export RUNNER_OS="$runner_name"
    fi
}

package_control_sync_required() {
    if [ ! -f "${ST_PACKAGES_DIR%/*}/Installed Packages/Package Control.sublime-package" ]; then
        return 0
    fi

    local dependency_fingerprint
    dependency_fingerprint="$(package_dependency_fingerprint)"
    if [ -z "$dependency_fingerprint" ]; then
        return 1
    fi

    [ "$(cat "$DEPENDENCY_MARKER_DIR/$PACKAGE.sha256" 2>/dev/null || true)" != "$dependency_fingerprint" ]
}

package_dependency_fingerprint() {
    local dependencies_file="$ST_PACKAGES_DIR/$PACKAGE/dependencies.json"
    if [ ! -f "$dependencies_file" ]; then
        return 0
    fi

    sha256sum "$dependencies_file" | awk '{ print $1 }'
}

write_package_dependency_marker() {
    local dependency_fingerprint
    dependency_fingerprint="$(package_dependency_fingerprint)"
    if [ -z "$dependency_fingerprint" ]; then
        return
    fi

    mkdir -p "$DEPENDENCY_MARKER_DIR"
    printf '%s\n' "$dependency_fingerprint" > "$DEPENDENCY_MARKER_DIR/$PACKAGE.sha256"
}

sudo sh -e /etc/init.d/xvfb start
ensure_git_identity
ensure_ci_platform_compat

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

NEEDS_PACKAGE_CONTROL_SYNC=false
if [ ! -f "$BOOTSTRAP_MARKER" ]; then
    # Bootstrap from a neutral cwd to avoid Windows worktree .git indirection
    # paths breaking git commands inside the Linux container.
    (cd /tmp && /docker.sh bootstrap skip_package_copy)
    NEEDS_PACKAGE_CONTROL_SYNC=true
fi

# Always refresh checked-out package into Packages/<PACKAGE> before syncing
# Package Control libraries, so dependencies.json from the package under test
# is visible to Package Control.
/docker.sh copy_tested_package overwrite

if package_control_sync_required; then
    NEEDS_PACKAGE_CONTROL_SYNC=true
fi

if [ "$NEEDS_PACKAGE_CONTROL_SYNC" = true ]; then
    /docker.sh install_package_control
    write_package_dependency_marker
    mkdir -p "$(dirname "$BOOTSTRAP_MARKER")"
    touch "$BOOTSTRAP_MARKER"
fi

if [ "$#" -gt 0 ]; then
    /docker.sh "$@"
else
    /docker.sh run_tests --coverage
fi
