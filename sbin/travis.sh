#!/bin/bash

set -e

if [ "$TRAVIS_OS_NAME" = "osx" ]; then
    STP="$HOME/Library/Application Support/Sublime Text $SUBLIME_TEXT_VERSION/Packages"
else
    STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
fi

Bootstrap() {
    STI_URL="https://github.com/randy3k/sublime_text_installer"
    git clone --quiet --depth 1 --branch master "$STI_URL" "$HOME/sublime_text_installer"

    sh "$HOME/sublime_text_installer/install_sublime_text.sh"

    if [ ! -d "$STP/$PACKAGE" ]; then
        echo "symlink the package to sublime package directory"
        ln -s "$PWD" "$STP/$PACKAGE"
    fi

    UT_URL="https://github.com/randy3k/UnitTesting"

    if [ -z $TAG ]; then
        # latest tag
        echo "download latest UnitTesting tag"
        TAG=$(git ls-remote --tags "$UT_URL" |
              sed 's|.*/\(.*\)$|\1|' | grep -v '\^' |
              sort -t. -k1,1nr -k2,2nr -k3,3nr | head -n1)
    fi

    if [ ! -d "$STP/UnitTesting" ]; then
        git clone --quiet --depth 1 --branch $TAG "$UT_URL" "$STP/UnitTesting"
    fi
}

InstallPackageControl() {
    STI_URL="https://github.com/randy3k/sublime_text_installer"
    if [ ! -d "$HOME/sublime_text_installer" ]; then
        git clone --quiet --depth 1 --branch master "$STI_URL" "$HOME/sublime_text_installer"
    fi
    sh "$HOME/sublime_text_installer/install_package_control.sh"
}

RunTests() {
    if [ "$TRAVIS_OS_NAME" = "linux" ] && [ -z $DISPLAY ]; then
        export DISPLAY=:99.0
        sh -e /etc/init.d/xvfb start
    fi

    if [ -z "$1" ]; then
        python "$STP/UnitTesting/sbin/run.py" "$PACKAGE"
    else
        python "$STP/UnitTesting/sbin/run.py" "$1" "$PACKAGE"
    fi
}

COMMAND=$1
echo "Running command: ${COMMAND}"
shift
case $COMMAND in
    "bootstrap")
        Bootstrap "$@"
        ;;
    "install_package_control")
        InstallPackageControl "$@"
        ;;
    "run_tests")
        RunTests "$@"
        ;;
    "run_syntax_tests")
        RunTests "--syntax-test" "$@"
        ;;
esac
