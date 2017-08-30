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

    if [ "$PACKAGE" = "__all__" ]; then
        echo "copy all subfolders to sublime package directory"
        mkdir -p "$STP"
        cp -r ./ "$STP"
    else
        if [ ! -d "$STP/$PACKAGE" ]; then
            # symlink does not play well with coverage
            echo "copy the package to sublime package directory"
            mkdir -p "$STP/$PACKAGE"
            cp -r ./ "$STP/$PACKAGE"
        fi
    fi

    # Disable warnings about detached HEAD
    # https://stackoverflow.com/questions/36794501
    git config --global advice.detachedHead false

    UT_PATH="$STP/UnitTesting"
    if [ ! -d "$UT_PATH" ]; then

        if [ -z $UT_URL ]; then
            UT_URL="https://github.com/randy3k/UnitTesting"
        fi

        if [ -z $UNITTESTING_TAG ]; then
            if [ $SUBLIME_TEXT_VERSION -eq 2 ]; then
                UNITTESTING_TAG="0.10.6"
            elif [ $SUBLIME_TEXT_VERSION -eq 3 ]; then
                # latest tag
                UNITTESTING_TAG=$(git ls-remote --tags "$UT_URL" |
                      sed 's|.*/\(.*\)$|\1|' | grep -v '\^' |
                      sort -t. -k1,1nr -k2,2nr -k3,3nr | head -n1)
            fi
        fi

        echo "download UnitTesting tag: $UNITTESTING_TAG"
        git clone --quiet --depth 1 --branch $UNITTESTING_TAG "$UT_URL" "$UT_PATH"
        git -C "$UT_PATH" rev-parse HEAD
        echo
    fi

    COV_PATH="$STP/coverage"
    if [ "$SUBLIME_TEXT_VERSION" -eq 3 ] && [ ! -d "$COV_PATH" ]; then

        COV_URL="https://github.com/codexns/sublime-coverage"

        if [ -z $COVERAGE_TAG ]; then
            # latest tag
            COVERAGE_TAG=$(git ls-remote --tags "$COV_URL" |
                  sed 's|.*/\(.*\)$|\1|' | grep -v '\^' |
                  sort -t. -k1,1nr -k2,2nr -k3,3nr | head -n1)
        fi

        echo "download sublime-coverage tag: $COVERAGE_TAG"
        git clone --quiet --depth 1 --branch $COVERAGE_TAG "$COV_URL" "$COV_PATH"
        git -C "$COV_PATH" rev-parse HEAD
        echo
        rm -rf "$COV_PATH/.git"
    fi

    if [ "$1" = "--with-color-scheme-unit" ]; then
        shift
        CSU_PATH="$STP/ColorSchemeUnit"
        if [ "$SUBLIME_TEXT_VERSION" -eq 3 ] && [ ! -d "$CSU_PATH" ]; then

            CSU="https://github.com/gerardroche/sublime-color-scheme-unit"

            if [ -z $COLOR_SCHEME_UNIT_TAG ]; then
                # latest tag
                COLOR_SCHEME_UNIT_TAG=$(git ls-remote --tags "$CSU" |
                      sed 's|.*/\(.*\)$|\1|' | grep -v '\^' |
                      sort -t. -k1,1nr -k2,2nr -k3,3nr | head -n1)
            fi

            echo "download ColorSchemeUnit tag: $COLOR_SCHEME_UNIT_TAG"
            git clone --quiet --depth 1 --branch $COLOR_SCHEME_UNIT_TAG "$CSU" "$CSU_PATH"
            git -C "$CSU_PATH" rev-parse HEAD
            echo
            rm -rf "$CSU_PATH/.git"
        fi
    fi

    sh "$STP/UnitTesting/sbin/install_sublime_text.sh"
}

InstallPackageControl() {
    if [ "$TRAVIS_OS_NAME" = "linux" ] && [ -z $DISPLAY ]; then
        export DISPLAY=:99.0
        sh -e /etc/init.d/xvfb start || true
    fi

    COV_PATH="$STP/coverage"
    rm -rf "$COV_PATH"

    sh "$STP/UnitTesting/sbin/install_package_control.sh"
}

RunTests() {
    if [ "$TRAVIS_OS_NAME" = "linux" ] && [ -z $DISPLAY ]; then
        export DISPLAY=:99.0
        sh -e /etc/init.d/xvfb start || true
        # The above statement prints a status message
        # but doesn't append a newline on the end.
        echo ""
    fi

    if [ -z "$1" ]; then
        python "$STP/UnitTesting/sbin/run_tests.py" "$PACKAGE"
    else
        python "$STP/UnitTesting/sbin/run_tests.py" "$@" "$PACKAGE"
    fi
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
    "run_tests")
        RunTests "$@"
        ;;
    "run_syntax_tests")
        RunTests "--syntax-test" "$@"
        ;;
    "run_color_scheme_tests")
        RunTests "--color-scheme-test" "$@"
        ;;
esac
