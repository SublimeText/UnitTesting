#!/bin/bash

# This script should be CI agnostic

set -e

SUBLIME_TEXT_VERSION=${SUBLIME_TEXT_VERSION:-3}
SUBLIME_TEXT_ARCH=${SUBLIME_TEXT_ARCH:-x64}

if [ $(uname) = 'Darwin' ]; then
    STP="$HOME/Library/Application Support/Sublime Text $SUBLIME_TEXT_VERSION/Packages"
else
    STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
fi

Bootstrap() {
    # Disable warnings about detached HEAD
    # https://stackoverflow.com/questions/36794501
    git config --global advice.detachedHead false

    # Copy plugin files to Packages/<Package> folder.
    if [ ! -d "$STP/$PACKAGE" ]; then
        # symlink does not play well with coverage
        echo "copy the package to sublime package directory"
        mkdir -p "$STP/$PACKAGE"
        cp -r ./ "$STP/$PACKAGE"
    fi

    local UT_PATH="$STP/UnitTesting"
    if [ ! -d "$UT_PATH" ]; then
        local UT_TAG=$(getLatestUnitTestingBuildTag \
            "$UNITTESTING_TAG" "$SUBLIME_TEXT_VERSION" "https://github.com/SublimeText/UnitTesting")
        InstallPackage "$UT_PATH" "$UT_TAG" "https://github.com/SublimeText/UnitTesting"
    fi

    InstallPackage "$STP/coverage" "$COVERAGE_TAG" "https://github.com/codexns/sublime-coverage"

    InstallSublimeText
}

gitGetHeadRevisionName() {
    git -C "$1" rev-parse HEAD
}

getLatestUnitTestingBuildTag() {
    local PreferredTag="$1"
    local SUBLIME_TEXT_VERSION="$2"
    local UrlToUnitTesting="$3"
    if [ -z "$PreferredTag" ]; then
        if [ $SUBLIME_TEXT_VERSION -eq 2 ]; then
            local TAG="0.10.6"
        else
            local TAG=$(gitFetchLatestTagFromRepository "$UrlToUnitTesting")
        fi
    else
        local TAG="$PreferredTag"
    fi
    echo "$TAG"
}

gitCloneTag() {
    local TAG="$1"
    local URL="$2"
    local DEST="$3"
    git clone --quiet --depth 1 --branch "$TAG" "$URL" "$DEST"
}

gitFetchLatestTagFromRepository() {
    local URL="$1"
    local LSTAGS
    LSTAGS=`git ls-remote --tags "$URL"`
    local TAG=$(echo "$LSTAGS" | grep -E '/v?[0-9]+\.[0-9]+\.[0-9]+$' |
      sed -E 's|.*/v?([^/]*)$|\1|' |
      sort -t. -k1,1nr -k2,2nr -k3,3nr | head -n1)
    echo "$LSTAGS" | grep -F "$TAG" | sed -E 's|.*/([^/]*)$|\1|' | grep -v '\^' | head -n1
}

getRepositoryTag() {
    local PreferredTag="$1"
    local URL="$2"
    if [ -z "$PreferredTag" ]; then
        local TAG=$(gitFetchLatestTagFromRepository "$URL")
    else
        local TAG="$PreferredTag"
    fi
    echo "$TAG"
}

cloneRepositoryTag() {
    local PreferredTag="$1"
    local URL="$2"
    local DEST="$3"
    local TAG=$(getRepositoryTag "$PreferredTag" "$URL")
    echo "cloning $URL tag: $TAG into $DEST..."
    gitCloneTag "$TAG" "$URL" "$DEST"
    gitGetHeadRevisionName "$DEST"
}

InstallPackage() {
    local DEST="$1"
    local PreferredTag="$2"
    local URL="$3"
    if [ ! -d "$DEST" ]; then
        mkdir -p "$DEST"
        cloneRepositoryTag "$PreferredTag" "$URL" "$DEST"
    fi
}

InstallColorSchemeUnit() {
    local CSU_PATH="$STP/ColorSchemeUnit"
    local CSU_URL="https://github.com/gerardroche/sublime-color-scheme-unit"
    if [ "$SUBLIME_TEXT_VERSION" -ge 3 ]; then
        InstallPackage "$CSU_PATH" "$COLOR_SCHEME_UNIT_TAG" "$CSU_URL"
    fi
}

InstallKeypress() {
    local KP_PATH="$STP/Keypress"
    local KP_URL="https://github.com/randy3k/Keypress"
    if [ "$SUBLIME_TEXT_VERSION" -ge 3 ]; then
        InstallPackage "$KP_PATH" "$KEYPRESS_TAG" "$KP_URL"
    fi
}

InstallSublimeText() {
    sh "$STP/UnitTesting/sbin/install_sublime_text.sh" "--st" "$SUBLIME_TEXT_VERSION"
}

InstallPackageControl() {
    COV_PATH="$STP/coverage"
    rm -rf "$COV_PATH"

    sh "$STP/UnitTesting/sbin/install_package_control.sh" "--st" "$SUBLIME_TEXT_VERSION"
}

RunTests() {
    if [ -z "$1" ]; then
        python "$STP/UnitTesting/sbin/run_tests.py" "$PACKAGE"
    else
        python "$STP/UnitTesting/sbin/run_tests.py" "$@" "$PACKAGE"
    fi

    pkill "[Ss]ubl" || true
    pkill 'plugin_host' || true
    sleep 1
}


COMMAND=$1
shift
echo "Running command: ${COMMAND} $@"
case $COMMAND in
    "bootstrap")
        Bootstrap "$@"
        ;;
    "install_package_control")
        InstallPackageControl "$@"
        ;;
    "install_color_scheme_unit")
        InstallColorSchemeUnit "$@"
        ;;
    "install_keypress")
        InstallKeypress "$@"
        ;;
    "run_tests")
        RunTests "$@"
        ;;
    "run_syntax_tests")
        RunTests "--syntax-test" "$@"
        ;;
    "run_syntax_compatibility")
        RunTests "--syntax-compatibility" "$@"
        ;;
    "run_color_scheme_tests")
        RunTests "--color-scheme-test" "$@"
        ;;
esac
