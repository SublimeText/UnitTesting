#!/bin/bash

set -e

Bootstrap() {
    if [ $(uname) == 'Darwin'  ]; then
        STP="$HOME/Library/Application Support/Sublime Text $SUBLIME_TEXT_VERSION/Packages"
        if [ -z $(which subl) ]; then
            brew install caskroom/cask/brew-cask
            if [ $SUBLIME_TEXT_VERSION -eq 2 ]; then
                echo installing sublime text 2
                brew cask install sublime-text
            elif [ $SUBLIME_TEXT_VERSION -eq 3 ]; then
                echo installing sublime text 3
                brew tap caskroom/versions
                brew cask install sublime-text3
            fi
        fi
    else
        STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
        if [ -z $(which subl) ]; then
            if [ $SUBLIME_TEXT_VERSION -eq 2 ]; then
                echo installing sublime text 2
                sudo add-apt-repository ppa:webupd8team/sublime-text-2 -y
                sudo apt-get update
                sudo apt-get install sublime-text -y
            elif [ $SUBLIME_TEXT_VERSION -eq 3 ]; then
                echo installing sublime text 3
                sudo add-apt-repository ppa:webupd8team/sublime-text-3 -y
                sudo apt-get update
                sudo apt-get install sublime-text-installer -y
            fi
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
        if [ -z $TAG ]; then
            # latest tag
            echo download latest UnitTesting tag
            TAG=$(git ls-remote --tags https://github.com/randy3k/UnitTesting.git | sed 's|.*/\(.*\)$|\1|' | grep -v '\^' | sort -t. -k1,1nr -k2,2nr -k3,3nr | head -n1)
        fi
        git clone --branch $TAG https://github.com/randy3k/UnitTesting "$STP/UnitTesting"
    fi
}

RunTests() {
    if [ $(uname) = 'Darwin' ]; then
        STP="$HOME/Library/Application Support/Sublime Text $SUBLIME_TEXT_VERSION/Packages"
        # for some unknown reasons, st cannot be launched by `subl` immediately
        # we have to open sublime first
        if [ $SUBLIME_TEXT_VERSION -eq 2 ]; then
            open "$HOME/Applications/Sublime Text 2.app"
            sleep 2
        elif [ $SUBLIME_TEXT_VERSION -eq 3 ]; then
            echo "about to open"
            open "$HOME/Applications/Sublime Text.app"
            sleep 2
            # to cancel update sublime message window
            osascript -e 'tell application "System Events" to key code 53'
            sleep 2
        fi
    else
        STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
        if [ -z $DISPLAY ]; then
            export DISPLAY=:99.0
            sh -e /etc/init.d/xvfb start
        fi
    fi
    UT="$STP/UnitTesting"
    if [ -z "$1" ]; then
        python "$UT/sbin/run.py" "$PACKAGE"
    else
        python "$UT/sbin/run.py" "$1" "$PACKAGE"
    fi
}

COMMAND=$1
echo "Running command: ${COMMAND}"
shift
case $COMMAND in
    "bootstrap")
        Bootstrap
        ;;
    "run_tests")
        RunTests "$@"
        ;;
esac
