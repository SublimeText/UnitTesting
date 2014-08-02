#!/bin/bash

set -e

Bootstrap() {
    STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
    if [ -z $(which subl) ]; then
        if [ $SUBLIME_TEXT_VERSION -eq 2 ]; then
            echo installing sublime 2
            sudo add-apt-repository ppa:webupd8team/sublime-text-2 -y
            sudo apt-get update
            sudo apt-get install sublime-text -y
        elif [ $SUBLIME_TEXT_VERSION -eq 3 ]; then
            echo installing sublime 3
            sudo add-apt-repository ppa:webupd8team/sublime-text-3 -y
            sudo apt-get update
            sudo apt-get install sublime-text-installer -y
        fi
    fi

    if [ ! -d "$STP" ]; then
        echo creating sublime package directory
        mkdir -p "$STP"
    fi

    if [ ! -d "$STP/$PACKAGE" ]; then
        echo symlink the package to sublime package directory
        ln -s "$PWD" "$STP/$PACKAGE"
    fi

    if [ ! -d "$STP/UnitTesting" ]; then
        echo download latest UnitTesting release
        # for stability, you may consider a fixed version of UnitTesting, eg TAG=0.1.4
        TAG=`git ls-remote --tags https://github.com/randy3k/UnitTesting | sed 's|.*/\([^/]*$\)|\1|' | sort -r -t . -n | head -1`
        git clone --branch $TAG https://github.com/randy3k/UnitTesting "$STP/UnitTesting"
    fi
}

RunTests() {
    if [ -z $DISPLAY ]; then
        export DISPLAY=:99.0
        sh -e /etc/init.d/xvfb start
    fi
    STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
    UT="$STP/UnitTesting"
    python "$UT/sbin/run.py" "$PACKAGE"
}

COMMAND=$1
echo "Running command: ${COMMAND}"
shift
case $COMMAND in
    "bootstrap")
        Bootstrap
        ;;
    "run_tests")
        RunTests
        ;;
esac
