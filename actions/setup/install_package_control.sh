#! /usr/bin/env bash

set -e

while [ "$#" -ne 0 ]; do
    key="$1"
    case "$key" in
        --st)
            SUBLIME_TEXT_VERSION="$2"
            shift 2
        ;;
        *)
            echo "Unknown option: $1"
            exit 1
        ;;
    esac
done

if [ -z $SUBLIME_TEXT_VERSION ]; then
    echo "missing Sublime Text version"
    exit 1
fi

if [ $SUBLIME_TEXT_VERSION -ge 4 ]; then
    if [ $(uname) = 'Darwin' ]; then
        STP="$HOME/Library/Application Support/Sublime Text/Packages"
    else
        STP="$HOME/.config/sublime-text/Packages"
    fi
else
    if [ $(uname) = 'Darwin' ]; then
        STP="$HOME/Library/Application Support/Sublime Text $SUBLIME_TEXT_VERSION/Packages"
    else
        STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
    fi
fi

STIP="${STP%/*}/Installed Packages"

if [ ! -d "$STIP" ]; then
    mkdir -p "$STIP"
fi

PC_PATH="$STIP/Package Control.sublime-package"
if [ ! -f "$PC_PATH" ]; then
    echo Downloading Package Control.sublime-package
    PC_URL="https://github.com/wbond/package_control/releases/latest/download/Package.Control.sublime-package"
    curl -s -L "$PC_URL" -o "$PC_PATH"
fi

if [ ! -f "$STP/User/Package Control.sublime-settings" ]; then
    echo Creating Package Control.sublime-settings
    [ ! -d "$STP/User" ] && mkdir -p "$STP/User"
    # make sure Pakcage Control does not complain
    echo '{"auto_upgrade": false, "ignore_vcs_packages": true, "remove_orphaned": false, "submit_usage": false }' > "$STP/User/Package Control.sublime-settings"
fi

PCH_PATH="$STP/0_install_package_control_helper"

if [ ! -d "$PCH_PATH" ]; then
    mkdir -p "$PCH_PATH"
    BASE=`dirname "$0"`
    cp "$BASE/install_package_control_helper.py" "$PCH_PATH/install_package_control_helper.py"
    cp "$BASE/.python-version" "$PCH_PATH/.python-version"
fi

# launch sublime text in background
echo Starting Sublime Text

for i in {1..3}; do
    subl &

    ENDTIME=$(( $(date +%s) + 60 ))
    while [ ! -f "$PCH_PATH/failed" ] && [ ! -f "$PCH_PATH/success" ] && [ $(date +%s) -lt $ENDTIME ] ; do
        printf "."
        sleep 5
    done

    sleep 2
    pkill subl || true
    sleep 2

    [ -f "$PCH_PATH/failed" ] && break
    [ -f "$PCH_PATH/success" ] && break
done

echo "" # add newline after progress dots
echo Terminated Sublime Text

if [ -f "$PCH_PATH/log" ]; then
    cat "$PCH_PATH/log"
fi

if [ ! -f "$PCH_PATH/success" ]; then
    echo "Timeout: Fail to install Package Control."
    rm -rf "$PCH_PATH"
    exit 1
fi

rm -rf "$PCH_PATH"

echo "Package Control installed."
