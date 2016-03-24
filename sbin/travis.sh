#!/bin/bash

set -e

Bootstrap() {
    if [ $(uname) = 'Darwin'  ]; then
        STP="$HOME/Library/Application Support/Sublime Text $SUBLIME_TEXT_VERSION/Packages"
        if [ -z $(which subl) ]; then
            brew update
            brew tap caskroom/cask
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
        mkdir -p "$STP/User"
        # disable update check
        echo '{"update_check": false }' > "$STP/User/Preferences.sublime-settings"
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
        git clone --quiet --depth 1 --branch $TAG https://github.com/randy3k/UnitTesting "$STP/UnitTesting"
    fi
}

OpenSubl() {
	# Do not open if already open
	ps aux | grep -iqE 'subl[^/]*(\s|$)' && return

	subl $@ &
	sleep 2
}

CloseSubl(){
	pkill -n '[sS]ubl'
	sleep 2
}

CycleUntil() {
	until eval "$1 2>/dev/null"; do
		echo Opening...
		OpenSubl
		echo Opened

		TOUT=0
		until eval "$1 2>/dev/null" || [ $TOUT -ge 30 ]; do
			sleep 1
			TOUT=`expr $TOUT + 1`
		done
		if [ $TOUT -ge 30 ]; then
			echo Timed out after 30s. Retrying...
		fi

		echo Closing...
		CloseSubl
		echo Closed
	done
}

RunTests() {
    if [ $(uname) = 'Darwin' ]; then
        STP="$HOME/Library/Application Support/Sublime Text $SUBLIME_TEXT_VERSION/Packages"
        # for some unknown reasons, st cannot be launched by `subl` immediately
        # we have to open sublime once
        if [ $SUBLIME_TEXT_VERSION -eq 2 ]; then
            open "$HOME/Applications/Sublime Text 2.app"
            sleep 2
            osascript -e 'tell application "Sublime Text 2" to quit' || true
            sleep 2
        elif [ $SUBLIME_TEXT_VERSION -eq 3 ]; then
            open "$HOME/Applications/Sublime Text.app"
            sleep 2
            osascript -e 'tell application "Sublime Text" to quit' || true
            sleep 2
        fi
    else
        STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
        if [ -z $DISPLAY ]; then
            export DISPLAY=:99.0
            sh -e /etc/init.d/xvfb start
        fi
    fi

	# Install dependencies through Package Control
	if [ -n $PCDEPS ]; then
		STIP="${STP%/*}/Installed Packages"
		if [ ! -d "$STIP" ]; then
			echo creating sublime installed package directory
			mkdir -p "$STIP"
		fi
	
		# Install PackageControl
		PC_URL="https://packagecontrol.io/Package Control.sublime-package"
		PC_PKG="${PC_URL##*/}"
		curl "$PC_URL" -o "$STIP/$PC_PKG"

		# Cycle ST to complete installation
		finished="! awk '/in_process_packages/,/]/' \
			'$STP/User/Package Control.sublime-settings' | tail -n +2 | grep -q \\\""

		echo Installing Package Control...
		CycleUntil "[ -f '$STP/User/Package Control.sublime-settings' ] && $finished"

		echo Opening Sublime until Package Control installs...
		CycleUntil "[ -d '$STP/bz2' ] && $finished"

		echo Installing dependencies...
		OpenSubl -b --command install_local_dependency
		sleep 5
		CycleUntil "$finished"

		echo Finished installing dependencies
	fi

	echo "Running tests now..."

	# Run tests
    UT="$STP/UnitTesting"
    if [ -z "$1" ]; then
        python "$UT/sbin/run.py" "$PACKAGE"
    else
        python "$UT/sbin/run.py" "$1" "$PACKAGE"
    fi
}

	echo "Command: $*"
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
    "run_syntax_tests")
        RunTests "--syntax-test" "$@"
        ;;
esac
