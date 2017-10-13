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

if [ $(uname) = 'Darwin' ]; then
    STP="$HOME/Library/Application Support/Sublime Text $SUBLIME_TEXT_VERSION/Packages"
else
    STP="$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages"
fi

STIP="${STP%/*}/Installed Packages"

if [ ! -d "$STIP" ]; then
    mkdir -p "$STIP"
fi

PC_PATH="$STIP/Package Control.sublime-package"
if [ ! -f "$PC_PATH" ]; then
    PC_URL="https://packagecontrol.io/Package Control.sublime-package"
    wget -O "$PC_PATH" "$PC_URL"
fi

PCH_PATH="$STP/0_install_package_control_helper"

if [ ! -d "$PCH_PATH" ]; then
    mkdir -p "$PCH_PATH"
    BASE=`dirname "$0"`
    cp "$BASE"/pc_helper.py "$PCH_PATH"/pc_helper.py
fi


# launch sublime text in background
for i in {1..2}; do
    subl &

    ENDTIME=$(( $(date +%s) + 60 ))
    while [ ! -f "$PCH_PATH/success" ] && [ $(date +%s) -lt $ENDTIME ]  ; do
        printf "."
        sleep 5
    done

    pkill "[Ss]ubl" || true
    killall 'plugin_host' || true
    sleep 2
    [ -f "$PCH_PATH/success" ] && break
done

if [ ! -f "$PCH_PATH/success" ]; then
    if [ -f "$PCH_PATH/log" ]; then
        cat "$PCH_PATH/log"
    fi
    echo "Timeout: Fail to install Package Control."
    rm -rf "$PCH_PATH"
    exit 1
fi

rm -rf "$PCH_PATH"
echo ""

if [ ! -f "$STP/User/Package Control.sublime-settings" ]; then
    echo creating Package Control.sublime-settings
    # make sure Pakcage Control does not complain
    echo '{"ignore_vcs_packages": true }' > "$STP/User/Package Control.sublime-settings"
fi

echo "Package Control installed."
