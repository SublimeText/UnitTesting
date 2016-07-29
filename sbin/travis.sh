#!/bin/bash

set -e

if [ "$TRAVIS_OS_NAME" = "osx" ]; then
    STP="$HOME/Library/Application Support/Sublime Text $SUBLIME_TEXT_VERSION/Packages"
else
    STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
fi

Bootstrap() {
    if [ "$TRAVIS_OS_NAME" = "linux" ] && [ -z $DISPLAY ]; then
        export DISPLAY=:99.0
        sh -e /etc/init.d/xvfb start || true
    fi

    STI_URL="https://github.com/randy3k/sublime_text_installer"
    git clone --quiet --depth 1 --branch master "$STI_URL" "$HOME/sublime_text_installer"

    sh "$HOME/sublime_text_installer/install_sublime_text.sh"

    if [ ! -d "$STP/$PACKAGE" ]; then
        # we need synlink to get correct file paths for coverage and coveralls
        echo "symlink the package to sublime package directory"
        mkdir -p "$STP/$PACKAGE"
        cp -r * "$STP/$PACKAGE"
    fi

    UT_PATH="$STP/UnitTesting"
    if [ ! -d "$UT_PATH" ]; then

        UT_URL="https://github.com/randy3k/UnitTesting"

        if [ -z $UNITTESTING_TAG ]; then
            # latest tag
            echo "download latest UnitTesting tag"
            UNITTESTING_TAG=$(git ls-remote --tags "$UT_URL" |
                  sed 's|.*/\(.*\)$|\1|' | grep -v '\^' |
                  sort -t. -k1,1nr -k2,2nr -k3,3nr | head -n1)
        fi

        git clone --quiet --depth 1 --branch $UNITTESTING_TAG "$UT_URL" "$UT_PATH"
    fi

    PR_PATH="$STP/PackageReloader"
    if [ "$SUBLIME_TEXT_VERSION" -eq 3 ] && [ ! -d "$PR_PATH" ]; then
        PR_URL="https://github.com/randy3k/PackageReloader"

        if [ -z $PACKAGE_RELOADER_TAG ]; then
            # latest tag
            PACKAGE_RELOADER_TAG=$(git ls-remote --tags "$PR_URL" |
                  sed 's|.*/v\(.*\)$|\1|' | grep -v '\^' |
                  sort -t. -k1,1nr -k2,2nr -k3,3nr | head -n1)
            PACKAGE_RELOADER_TAG="v$PACKAGE_RELOADER_TAG"
            echo "download latest PackageReloader tag: $PACKAGE_RELOADER_TAG"
        fi

        git clone --quiet --depth 1 --branch $PACKAGE_RELOADER_TAG "$PR_URL" "$PR_PATH"
        rm -rf "$PR_PATH/.git"
    fi

    COV_PATH="$STP/coverage"
    if [ "$SUBLIME_TEXT_VERSION" -eq 3 ] && [ ! -d "$COV_PATH" ]; then

        COV_URL="https://github.com/codexns/sublime-coverage"

        if [ -z $COVERAGE_TAG ]; then
            # latest tag
            COVERAGE_TAG=$(git ls-remote --tags "$COV_URL" |
                  sed 's|.*/\(.*\)$|\1|' | grep -v '\^' |
                  sort -t. -k1,1nr -k2,2nr -k3,3nr | head -n1)
            echo "download latest sublime-coverage tag: $COVERAGE_TAG"
        fi

        git clone --quiet --depth 1 --branch $COVERAGE_TAG "$COV_URL" "$COV_PATH"
        rm -rf "$COV_PATH/.git"
    fi
}

InstallPackageControl() {
    if [ "$TRAVIS_OS_NAME" = "linux" ] && [ -z $DISPLAY ]; then
        export DISPLAY=:99.0
        sh -e /etc/init.d/xvfb start || true
    fi

    STI_URL="https://github.com/randy3k/sublime_text_installer"
    if [ ! -d "$HOME/sublime_text_installer" ]; then
        git clone --quiet --depth 1 --branch master "$STI_URL" "$HOME/sublime_text_installer"
    fi
    sh "$HOME/sublime_text_installer/install_package_control.sh"
}

RunTests() {
    if [ "$TRAVIS_OS_NAME" = "linux" ] && [ -z $DISPLAY ]; then
        export DISPLAY=:99.0
        sh -e /etc/init.d/xvfb start || true
    fi

    if [ -z "$1" ]; then
        python "$STP/UnitTesting/sbin/run_tests.py" "$PACKAGE"
    else
        python "$STP/UnitTesting/sbin/run_tests.py" "$1" "$PACKAGE"
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
